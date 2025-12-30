from typing import Sequence, Type
from uuid import UUID

from shop_project.application.shared.dto.mapper import to_dto
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.application.shared.schemas.product_schema import ProductSchema
from shop_project.domain.entities.product import Product


class CatalogueCustomerReadService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type

    async def get_products_by_ids(self, ids: list[UUID]) -> list[ProductSchema]:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=False)
            .load(Product)
            .from_id(ids)
            .no_lock()
            .build()
        ) as uow:
            resources = uow.get_resources()
            products: Sequence[Product] = resources.get_all(Product)

        res = [ProductSchema.model_validate(to_dto(product)) for product in products]

        return res

    async def get_products(self, offset: int, limit: int) -> list[ProductSchema]:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=False)
            .load(Product)
            .order_by("entity_id", desc=True)
            .offset(offset)
            .limit(limit)
            .no_lock()
            .build()
        ) as uow:
            resources = uow.get_resources()
            products: Sequence[Product] = resources.get_all(Product)

        res = [ProductSchema.model_validate(to_dto(product)) for product in products]

        return res
