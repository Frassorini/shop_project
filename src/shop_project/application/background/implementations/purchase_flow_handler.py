from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Sequence, Type
from uuid import UUID

from shop_project.application.background.base_task_handler import (
    BaseTaskHandler,
    NullTaskParams,
)
from shop_project.application.background.exceptions import RetryException
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
from shop_project.infrastructure.entities.task import Task


async def _get_state_map(
    payment_gateway: IPaymentGateway, escrow_accounts: Sequence[EscrowAccount]
) -> dict[PaymentState, list[EscrowAccount]]:
    fetched_states = await payment_gateway.get_states(
        [str(escrow_account.entity_id) for escrow_account in escrow_accounts]
    )

    state_map: dict[PaymentState, list[EscrowAccount]] = {}
    for escrow_account in escrow_accounts:
        state = fetched_states[str(escrow_account.entity_id)]
        state_map.setdefault(state, []).append(escrow_account)

    return state_map


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
            resources = uow.get_resorces()

            task = resources.get_by_id_or_none(Task, task_id)
            if task is None:
                return

            state_map = await _get_state_map(
                self._payment_gateway, resources.get_all(EscrowAccount)
            )

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

            uow.mark_commit()

        for unexpected_state in set(state_map) - {
            PaymentState.NONEXISTENT,
            PaymentState.PAID,
            PaymentState.CANCELLED,
        }:
            raise ValueError(
                f"Unexpected escrow account state: {unexpected_state}"
            )  # TODO: alert


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
            resources = uow.get_resorces()

            task = resources.get_by_id_or_none(Task, task_id)
            if task is None:
                return

            escrow_accounts = resources.get_all(EscrowAccount)
            purchases = resources.get_all(PurchaseActive)
            product_inventory = ProductInventory(resources.get_all(Product))

            escrow_purchase_map: dict[UUID, list[Any]] = defaultdict(
                lambda: [None, None]
            )

            for escrow_account in escrow_accounts:
                escrow_purchase_map[escrow_account.entity_id][0] = escrow_account

            for purchase in purchases:
                escrow_purchase_map[purchase.entity_id][1] = purchase

            for escrow, purchase in escrow_purchase_map.values():
                assert isinstance(purchase, PurchaseActive)
                assert isinstance(escrow, EscrowAccount)

                summary = self._purchase_return_service.handle_cancelled_payment(
                    product_inventory=product_inventory,
                    purchase_active=purchase,
                    escrow_account=escrow,
                )

                resources.delete(PurchaseActive, purchase)
                resources.put(PurchaseSummary, summary)

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
            .lesser_than("reserved_until", datetime.now(tz=timezone.utc))
            .for_update()
            .load(Product)
            .from_previous()
            .for_update()
            .build(),
            exception_on_nowait=RetryException,
        ) as uow:
            resources = uow.get_resorces()

            task = resources.get_by_id_or_none(Task, task_id)
            if task is None:
                return

            escrow_accounts = resources.get_all(EscrowAccount)
            purchases = resources.get_all(PurchaseActive)
            product_inventory = ProductInventory(resources.get_all(Product))

            escrow_purchase_map: dict[UUID, list[Any]] = defaultdict(
                lambda: [None, None]
            )

            for escrow_account in escrow_accounts:
                escrow_purchase_map[escrow_account.entity_id][0] = escrow_account

            for purchase in purchases:
                escrow_purchase_map[purchase.entity_id][1] = purchase

            for escrow, purchase in escrow_purchase_map.values():
                if not escrow:
                    continue

                assert isinstance(purchase, PurchaseActive)
                assert isinstance(escrow, EscrowAccount)

                summary = self._purchase_return_service.unclaim(
                    product_inventory=product_inventory,
                    purchase_active=purchase,
                    escrow_account=escrow,
                )

                resources.delete(PurchaseActive, purchase)
                resources.put(PurchaseSummary, summary)

            uow.mark_commit()

        await self._payment_gateway.start_refunds(
            [str(item.entity_id) for item in escrow_accounts if item]
        )


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
            resources = uow.get_resorces()

            task = resources.get_by_id_or_none(Task, task_id)
            if task is None:
                return

            state_map = await _get_state_map(
                self._payment_gateway, resources.get_all(EscrowAccount)
            )

            for escrow_account in state_map.get(PaymentState.REFUNDED, []):
                escrow_account.finalize()

            await self._payment_gateway.start_refunds(
                [str(item.entity_id) for item in state_map.get(PaymentState.PAID, [])]
            )

            uow.mark_commit()

        for unexpected_state in set(state_map) - {
            PaymentState.REFUNDING,
            PaymentState.REFUNDED,
            PaymentState.PAID,
        }:
            raise ValueError(
                f"Unexpected escrow account state: {unexpected_state}"
            )  # TODO: alert
