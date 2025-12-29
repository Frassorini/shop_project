from datetime import datetime, timezone
from typing import Any, Type
from uuid import UUID

from shop_project.application.background.base_task_handler import (
    BaseTaskHandler,
    NullTaskParams,
)
from shop_project.application.entities.task import Task
from shop_project.application.exceptions import RetryException
from shop_project.application.shared.dto.mapper import to_dto
from shop_project.application.shared.interfaces.interface_payment_gateway import (
    CreatePaymentRequest,
    IPaymentGateway,
    PaymentState,
)
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.application.shared.operation_log_payload_factories.purchase import (
    create_auto_unclaim_purchase_payload,
    create_cancel_purchase_payload,
    create_pay_purchase_payload,
    create_refund_purchase_payload,
)
from shop_project.application.shared.scenarios.operation_log import log_operation
from shop_project.application.shared.scenarios.payment import (
    get_payment_state_map,
)
from shop_project.application.shared.scenarios.purchase import (
    get_escrow_purchase_active_map,
)
from shop_project.application.shared.scenarios.task import capture_task
from shop_project.domain.entities.escrow_account import (
    EscrowAccount,
    EscrowAccountState,
)
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.purchase_activation_service import (
    PurchaseActivationService,
)
from shop_project.domain.services.purchase_claim_service import PurchaseClaimService
from shop_project.domain.services.purchase_return_service import PurchaseReturnService


class BatchWaitPaymentTaskHandler(BaseTaskHandler[NullTaskParams]):
    handler_name = "batch_wait_payment"

    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        payment_gateway: IPaymentGateway,
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type
        self._purchase_activation_service: PurchaseActivationService = (
            purchase_activation_service
        )
        self._purchase_claim_service: PurchaseClaimService = purchase_claim_service
        self._purchase_return_service: PurchaseReturnService = purchase_return_service
        self._payment_gateway: IPaymentGateway = payment_gateway

    async def handle(self, task_id: UUID) -> None:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Task)
            .from_attribute("entity_id", [task_id])
            .for_update(no_wait=True)
            .load(EscrowAccount)
            .from_attribute("state", [EscrowAccountState.PENDING.value])
            .for_update()
            .build(),
            exception_on_nowait=RetryException,
        ) as uow:
            resources = uow.get_resources()
            capture_task(resources, task_id)
            state_map = await get_payment_state_map(resources, self._payment_gateway)

            for escrow_account in state_map.get(PaymentState.PAID, []):
                escrow_account.mark_as_paid()

            for escrow_account in state_map.get(PaymentState.CANCELLED, []):
                escrow_account.cancel_payment()

            await self._payment_gateway.create_payments(
                [
                    CreatePaymentRequest(
                        payment_id=str(escrow_account.entity_id),
                        amount=escrow_account.total_amount,
                    )
                    for escrow_account in state_map.get(PaymentState.NONEXISTENT, [])
                ]
            )

            for escrow_account in state_map.get(PaymentState.PAID, []):
                operation_log = create_pay_purchase_payload(to_dto(escrow_account))
                log_operation(resources, operation_log)

            uow.mark_commit()

        _handle_unexpected_states(
            state_map,
            {
                PaymentState.PAID,
                PaymentState.CANCELLED,
                PaymentState.NONEXISTENT,
            },
        )


class BatchFinalizeNotPaidTasksHandler(BaseTaskHandler[NullTaskParams]):
    handler_name = "batch_finalize_not_paid"

    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        payment_gateway: IPaymentGateway,
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type
        self._purchase_activation_service: PurchaseActivationService = (
            purchase_activation_service
        )
        self._purchase_claim_service: PurchaseClaimService = purchase_claim_service
        self._purchase_return_service: PurchaseReturnService = purchase_return_service
        self._payment_gateway: IPaymentGateway = payment_gateway

    async def handle(self, task_id: UUID) -> None:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Task)
            .from_attribute("entity_id", [task_id])
            .for_update(no_wait=True)
            .load(EscrowAccount)
            .from_attribute("state", [EscrowAccountState.PAYMENT_CANCELLED.value])
            .for_update()
            .load(PurchaseActive)
            .from_previous()
            .for_update()
            .load(Product)
            .from_previous()
            .for_update()
            .build(),
            exception_on_nowait=RetryException,
        ) as uow:
            resources = uow.get_resources()
            capture_task(resources, task_id)

            escrow_purchase_map: list[tuple[EscrowAccount, PurchaseActive]] = (
                get_escrow_purchase_active_map(resources)
            )
            product_inventory = ProductInventory(resources.get_all(Product))

            for escrow, purchase in escrow_purchase_map:
                summary = self._purchase_return_service.handle_cancelled_payment(
                    product_inventory=product_inventory,
                    purchase_active=purchase,
                    escrow_account=escrow,
                )
                resources.delete(PurchaseActive, purchase)
                resources.put(PurchaseSummary, summary)

            for escrow, purchase in escrow_purchase_map:
                operation_log = create_cancel_purchase_payload(to_dto(escrow))
                log_operation(resources, operation_log)

            uow.mark_commit()


class BatchPaidReservationTimeOutTaskHandler(BaseTaskHandler[NullTaskParams]):
    handler_name = "batch_paid_reservation_time_out"

    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        payment_gateway: IPaymentGateway,
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type
        self._purchase_activation_service: PurchaseActivationService = (
            purchase_activation_service
        )
        self._purchase_claim_service: PurchaseClaimService = purchase_claim_service
        self._purchase_return_service: PurchaseReturnService = purchase_return_service
        self._payment_gateway: IPaymentGateway = payment_gateway

    async def handle(self, task_id: UUID) -> None:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Task)
            .from_attribute("entity_id", [task_id])
            .for_update(no_wait=True)
            .load(EscrowAccount)
            .from_attribute("state", [EscrowAccountState.PAID.value])
            .for_update()
            .load(PurchaseActive)
            .from_previous()
            .and_()
            .less_than("reserved_until", datetime.now(tz=timezone.utc))
            .for_update()
            .load(Product)
            .from_previous()
            .for_update()
            .build(),
            exception_on_nowait=RetryException,
        ) as uow:
            resources = uow.get_resources()
            capture_task(resources, task_id)

            escrow_purchase_map: list[tuple[EscrowAccount, PurchaseActive]] = (
                get_escrow_purchase_active_map(resources)
            )
            product_inventory = ProductInventory(resources.get_all(Product))

            for escrow, purchase in escrow_purchase_map:
                summary = self._purchase_return_service.unclaim(
                    product_inventory=product_inventory,
                    purchase_active=purchase,
                    escrow_account=escrow,
                )

                resources.delete(PurchaseActive, purchase)
                resources.put(PurchaseSummary, summary)

            await self._payment_gateway.start_refunds(
                [str(item[0].entity_id) for item in escrow_purchase_map]
            )

            for escrow, _ in escrow_purchase_map:
                summary: PurchaseSummary = resources.get_one_by_attribute(
                    PurchaseSummary, "escrow_account_id", escrow.entity_id
                )
                operation_log = create_auto_unclaim_purchase_payload(
                    purchase_summary_dto=to_dto(summary),
                    escrow_account_dto=to_dto(escrow),
                )
                log_operation(resources, operation_log)

            uow.mark_commit()

            uow.mark_commit()


class BatchWaitRefundTaskHandler(BaseTaskHandler[NullTaskParams]):
    handler_name = "batch_wait_refund"

    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        payment_gateway: IPaymentGateway,
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type
        self._purchase_activation_service: PurchaseActivationService = (
            purchase_activation_service
        )
        self._purchase_claim_service: PurchaseClaimService = purchase_claim_service
        self._purchase_return_service: PurchaseReturnService = purchase_return_service
        self._payment_gateway: IPaymentGateway = payment_gateway

    async def handle(self, task_id: UUID) -> None:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Task)
            .from_attribute("entity_id", [task_id])
            .for_update(no_wait=True)
            .load(EscrowAccount)
            .from_attribute("state", [EscrowAccountState.REFUNDING.value])
            .for_update()
            .build(),
            exception_on_nowait=RetryException,
        ) as uow:
            resources = uow.get_resources()
            capture_task(resources, task_id)

            state_map = await get_payment_state_map(resources, self._payment_gateway)

            for escrow_account in state_map.get(PaymentState.REFUNDED, []):
                escrow_account.finalize()

            await self._payment_gateway.start_refunds(
                [str(item.entity_id) for item in state_map.get(PaymentState.PAID, [])]
            )

            for escrow_account in state_map.get(PaymentState.REFUNDED, []):
                operation_log = create_refund_purchase_payload(to_dto(escrow_account))
                log_operation(resources, operation_log)

            uow.mark_commit()

        _handle_unexpected_states(
            state_map,
            {
                PaymentState.REFUNDED,
                PaymentState.REFUNDED,
                PaymentState.PAID,
            },
        )


def _handle_unexpected_states(
    state_map: dict[PaymentState, list[Any]], expected_states: set[PaymentState]
) -> None:
    for unexpected_state in set(state_map) - expected_states:
        raise ValueError(
            f"Unexpected escrow account state: {unexpected_state}"
        )  # TODO: alert
