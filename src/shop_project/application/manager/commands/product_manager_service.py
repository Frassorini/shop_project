from typing import Type
from uuid import UUID, uuid4

from shop_project.application.exceptions import ApplicationNotFoundError
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.dto.mapper import to_dto
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.application.shared.operation_log_payload_factories.product import (
    create_create_product_payload,
    create_delete_product_payload,
    create_update_product_payload,
)
from shop_project.application.shared.scenarios.entity import (
    get_one_or_raise_forbidden,
    get_one_or_raise_not_found,
)
from shop_project.application.shared.scenarios.operation_log import log_operation
from shop_project.application.shared.scenarios.subject import (
    ensure_subject_type_or_raise_forbidden,
)
from shop_project.application.shared.schemas.product_schema import (
    ChangeProductSchema,
    CreateProductSchema,
    ProductSchema,
)
from shop_project.domain.entities.manager import Manager
from shop_project.domain.entities.product import Product
from shop_project.domain.interfaces.subject import SubjectEnum


class ProductManagerService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type

    async def create_product(
        self, access_payload: AccessTokenPayload, product_schema: CreateProductSchema
    ) -> ProductSchema:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.MANAGER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Manager)
            .from_id([access_payload.account_id])
            .for_share()
            .build()
        ) as uow:
            resources = uow.get_resources()
            manager = get_one_or_raise_forbidden(
                resources, Manager, access_payload.account_id
            )

            product = Product(
                entity_id=uuid4(),
                name=product_schema.name,
                amount=product_schema.amount,
                price=product_schema.price,
            )

            resources.put(Product, product)

            operation_log = create_create_product_payload(
                access_payload, to_dto(product)
            )
            log_operation(resources, operation_log)

            uow.mark_commit()

        return ProductSchema.model_validate(to_dto(product))

    async def delete_products(
        self, access_payload: AccessTokenPayload, product_ids: list[UUID]
    ) -> None:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.MANAGER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Manager)
            .from_id([access_payload.account_id])
            .for_share()
            .load(Product)
            .from_id(product_ids)
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            manager = get_one_or_raise_forbidden(
                resources, Manager, access_payload.account_id
            )
            products = resources.get_all(Product)

            found_ids = {product.entity_id for product in products}
            if found_ids != set(product_ids):
                raise ApplicationNotFoundError(
                    f"Products {set(product_ids) - found_ids} not found"
                )

            for product in products:
                resources.delete(Product, product)

            for product in products:
                operation_log = create_delete_product_payload(
                    access_payload, to_dto(product)
                )
                log_operation(resources, operation_log)

            uow.mark_commit()

    async def change_product(
        self, access_payload: AccessTokenPayload, change: ChangeProductSchema
    ) -> ProductSchema:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.MANAGER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Manager)
            .from_id([access_payload.account_id])
            .for_share()
            .load(Product)
            .from_id([change.entity_id])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            manager = get_one_or_raise_forbidden(
                resources, Manager, access_payload.account_id
            )
            product = get_one_or_raise_not_found(resources, Product, change.entity_id)

            product.name = change.name
            product.price = change.price

            operation_log = create_update_product_payload(
                access_payload, to_dto(product)
            )
            log_operation(resources, operation_log)

            uow.mark_commit()

        return ProductSchema.model_validate(to_dto(product))
