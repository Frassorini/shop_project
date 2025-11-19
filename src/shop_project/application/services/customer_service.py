from typing import Type
from uuid import UUID

from shop_project.application.dto.mapper import to_dto
from shop_project.application.interfaces.interface_query_builder import IQueryBuilder
from shop_project.application.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.application.schemas.customer_schema_default import (
    CustomerSchemaDefault,
)
from shop_project.domain.entities.customer import Customer
from shop_project.shared.entity_id import EntityId


class CustomerService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type

    async def read_by_id(self, ids: list[UUID]) -> list[CustomerSchemaDefault]:
        entity_ids = [EntityId(id) for id in ids]
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=False)
            .load(Customer)
            .from_id(ids)
            .no_lock()
            .build()
        ) as uow:
            resources = uow.get_resorces()
            res: list[Customer] = resources.get_by_ids(Customer, entity_ids)

        return [CustomerSchemaDefault.create(to_dto(customer)) for customer in res]
