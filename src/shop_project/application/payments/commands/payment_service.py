from typing import Type
from uuid import UUID

from shop_project.application.shared.dto.mapper import to_dto
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.application.shared.operation_log_payload_factories.purchase import (
    create_cancel_purchase_payload,
    create_finalize_cancelled_purchase_payload,
    create_pay_purchase_payload,
    create_refund_purchase_payload,
)
from shop_project.application.shared.scenarios.entity import (
    get_one_or_raise_not_found,
)
from shop_project.application.shared.scenarios.operation_log import log_operation
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.domain.exceptions import DomainException
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.purchase_return_service import PurchaseReturnService


class PaymentService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_return_service: PurchaseReturnService,
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type
        self._purchase_return_service: PurchaseReturnService = purchase_return_service

    async def confirm_payment(self, purchase_id: UUID) -> None:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(EscrowAccount)
            .from_id([purchase_id])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            escrow: EscrowAccount = get_one_or_raise_not_found(
                resources, EscrowAccount, purchase_id
            )

            escrow.mark_as_paid()

            operation_log = create_pay_purchase_payload(to_dto(escrow))
            log_operation(resources, operation_log)

            uow.mark_commit()

    async def cancel_payment(self, purchase_id: UUID) -> None:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(EscrowAccount)
            .from_id([purchase_id])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            escrow: EscrowAccount = get_one_or_raise_not_found(
                resources, EscrowAccount, purchase_id
            )

            escrow.cancel_payment()

            operation_log = create_cancel_purchase_payload(to_dto(escrow))
            log_operation(resources, operation_log)

            uow.mark_commit()

    async def confirm_refund(self, purchase_id: UUID) -> None:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(EscrowAccount)
            .from_id([purchase_id])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            escrow: EscrowAccount = get_one_or_raise_not_found(
                resources, EscrowAccount, purchase_id
            )

            if not escrow.is_refunding():
                raise DomainException("Escrow account is not refunding")

            escrow.finalize()

            operation_log = create_refund_purchase_payload(to_dto(escrow))
            log_operation(resources, operation_log)

            uow.mark_commit()

    async def finalize_not_paid(self, purchase_id: UUID) -> None:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(EscrowAccount)
            .from_id([purchase_id])
            .for_update()
            .load(PurchaseActive)
            .from_previous()
            .for_update()
            .load(Product)
            .from_previous()
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            escrow: EscrowAccount = get_one_or_raise_not_found(
                resources, EscrowAccount, purchase_id
            )
            purchase: PurchaseActive = get_one_or_raise_not_found(
                resources, PurchaseActive, purchase_id
            )

            product_inventory = ProductInventory(resources.get_all(Product))

            summary = self._purchase_return_service.handle_cancelled_payment(
                escrow_account=escrow,
                product_inventory=product_inventory,
                purchase_active=purchase,
            )

            resources.delete(PurchaseActive, purchase)
            resources.put(PurchaseSummary, summary)

            operation_log = create_finalize_cancelled_purchase_payload(
                to_dto(escrow),
                to_dto(summary),
            )
            log_operation(resources, operation_log)

            uow.mark_commit()
