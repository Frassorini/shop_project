from typing import Callable, Coroutine, Type, cast

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.dto.mapper import to_dto
from shop_project.application.schemas.customer_schema_default import (
    CustomerSchemaDefault,
)
from shop_project.application.services.customer_service import CustomerService
from shop_project.domain.entities.customer import Customer
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from tests.helpers import AggregateContainer


@pytest.mark.asyncio
async def test_customer(
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    async_container: AsyncContainer,
) -> None:
    model_type: Type[PersistableEntity] = Customer
    domain_container: AggregateContainer = await prepare_container(model_type)
    aggregate: Customer = cast(Customer, domain_container.aggregate)

    service = await async_container.get(CustomerService)

    result: list[CustomerSchemaDefault] = await service.read_by_id(
        [aggregate.entity_id.value]
    )

    assert len(result) == 1
    assert result[0] == CustomerSchemaDefault.create(to_dto(aggregate))
