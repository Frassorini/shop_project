from typing import Type
from uuid import UUID

from shop_project.application.customer.schemas.purchase_active_schema import (
    PurchaseActiveSchema,
)
from shop_project.application.customer.schemas.purchase_draft_schema import (
    PurchaseDraftSchema,
)
from shop_project.application.customer.schemas.purchase_summary_schema import (
    PurchaseSummarySchema,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.dto.mapper import to_dto
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.application.shared.scenarios.entity import get_all_or_raise_not_found
from shop_project.application.shared.scenarios.purchase import (
    get_escrow_purchase_active_map,
    get_escrow_purchase_summary_map,
)
from shop_project.application.shared.scenarios.subject import (
    ensure_subject_type_or_raise_forbidden,
)
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.domain.interfaces.subject import SubjectEnum


class PurchaseCustomerReadService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type

    async def get_actives_by_ids(
        self, access_payload: AccessTokenPayload, ids: list[UUID]
    ) -> list[PurchaseActiveSchema]:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.CUSTOMER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=False)
            .load(EscrowAccount)
            .from_id(ids)
            .no_lock()
            .load(PurchaseActive)
            .from_previous()
            .and_()
            .from_attribute("customer_id", [access_payload.account_id])
            .no_lock()
            .build()
        ) as uow:
            resources = uow.get_resources()

            purchase_actives = get_all_or_raise_not_found(resources, PurchaseActive)
            escrow_accounts = get_all_or_raise_not_found(resources, EscrowAccount)

            escrow_purchase_map = get_escrow_purchase_active_map(resources)

        res = [
            PurchaseActiveSchema.create(
                purchase_summary_dto=to_dto(purchase_active),
                escrow_account_dto=to_dto(escrow_account),
            )
            for escrow_account, purchase_active in escrow_purchase_map
        ]

        return res

    async def get_drafts_by_ids(
        self, access_payload: AccessTokenPayload, ids: list[UUID]
    ) -> list[PurchaseDraftSchema]:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.CUSTOMER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=False)
            .load(PurchaseDraft)
            .from_id(ids)
            .no_lock()
            .load(Product)
            .from_previous()
            .no_lock()
            .build()
        ) as uow:
            resources = uow.get_resources()

            purchase_drafts = get_all_or_raise_not_found(resources, PurchaseDraft)
            products = resources.get_all(Product)

        res = [
            PurchaseDraftSchema.create(
                purchase_draft_dto=to_dto(purchase_draft),
                products=[to_dto(product) for product in products],
            )
            for purchase_draft in purchase_drafts
        ]

        return res

    async def get_summaries_by_ids(
        self, access_payload: AccessTokenPayload, ids: list[UUID]
    ) -> list[PurchaseSummarySchema]:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.CUSTOMER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=False)
            .load(EscrowAccount)
            .from_id(ids)
            .no_lock()
            .load(PurchaseSummary)
            .from_previous()
            .and_()
            .from_attribute("customer_id", [access_payload.account_id])
            .no_lock()
            .build()
        ) as uow:
            resources = uow.get_resources()

            purchase_summaries = get_all_or_raise_not_found(resources, PurchaseSummary)
            escrow_accounts = get_all_or_raise_not_found(resources, EscrowAccount)

            escrow_purchase_map = get_escrow_purchase_summary_map(resources)

        res = [
            PurchaseSummarySchema.create(
                purchase_summary_dto=to_dto(purchase_summary),
                escrow_account_dto=to_dto(escrow_account),
            )
            for escrow_account, purchase_summary in escrow_purchase_map
        ]

        return res
