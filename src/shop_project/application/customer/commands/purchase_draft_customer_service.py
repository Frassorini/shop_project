from typing import Type
from uuid import UUID, uuid4

from shop_project.application.customer.schemas.purchase_draft_schema import (
    PurchaseDraftSchema,
    SetNewPurchaseDraftItemsSchema,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.dto.mapper import to_dto
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.application.shared.scenarios.entity import (
    get_one_or_raise_forbidden,
    get_one_or_raise_not_found,
)
from shop_project.application.shared.scenarios.subject import (
    ensure_subject_type_or_raise_forbidden,
)
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.interfaces.subject import SubjectEnum


class PurchaseDraftCustomerService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type

    async def create_draft(
        self, access_payload: AccessTokenPayload
    ) -> PurchaseDraftSchema:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.CUSTOMER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Customer)
            .from_id([access_payload.account_id])
            .for_share()
            .build()
        ) as uow:
            resources = uow.get_resources()
            customer = get_one_or_raise_forbidden(
                resources, Customer, access_payload.account_id
            )

            purchase_draft = PurchaseDraft(uuid4(), customer.entity_id)
            resources.put(PurchaseDraft, purchase_draft)

            uow.mark_commit()

        return PurchaseDraftSchema.create(to_dto(purchase_draft), [])

    async def delete_draft(
        self, access_payload: AccessTokenPayload, draft_id: UUID
    ) -> None:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.CUSTOMER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Customer)
            .from_id([access_payload.account_id])
            .for_share()
            .load(PurchaseDraft)
            .from_id([draft_id])
            .and_()
            .from_attribute("customer_id", [access_payload.account_id])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            customer = get_one_or_raise_forbidden(
                resources, Customer, access_payload.account_id
            )
            purchase_draft = get_one_or_raise_not_found(
                resources, PurchaseDraft, draft_id
            )

            resources.delete(PurchaseDraft, purchase_draft)

            uow.mark_commit()

    async def change_products(
        self,
        access_payload: AccessTokenPayload,
        draft_id: UUID,
        change: SetNewPurchaseDraftItemsSchema,
    ) -> PurchaseDraftSchema:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.CUSTOMER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Customer)
            .from_id([access_payload.account_id])
            .for_share()
            .load(PurchaseDraft)
            .from_id([draft_id])
            .and_()
            .from_attribute("customer_id", [access_payload.account_id])
            .for_update()
            .load(Product)
            .from_id([item.product_id for item in change.items])
            .for_share()
            .build()
        ) as uow:
            resources = uow.get_resources()
            customer = get_one_or_raise_forbidden(
                resources, Customer, access_payload.account_id
            )
            purchase_draft = get_one_or_raise_not_found(
                resources, PurchaseDraft, draft_id
            )
            products = resources.get_all(Product)

            for item in purchase_draft.items:
                purchase_draft.remove_item(item.product_id)

            for item in change.items:
                product = resources.get_by_id_or_none(Product, item.product_id)
                if not product:
                    continue

                purchase_draft.add_item(item.product_id, item.amount)

            uow.mark_commit()

        return PurchaseDraftSchema.create(
            to_dto(purchase_draft), [to_dto(product) for product in products]
        )
