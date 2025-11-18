from shop_project.application.dto.mapper import to_dto
from shop_project.application.schemas.customer_schema_default import CustomerSchemaDefault


from decimal import Decimal
from typing import Any, Awaitable, Callable, Coroutine, Literal, Type, TypeVar, cast

from sqlalchemy.ext.asyncio import AsyncSession
from dishka.async_container import AsyncContainer
import pytest

from shop_project.application.services.customer_service import CustomerService

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.customer import Customer

from tests.helpers import AggregateContainer


@pytest.mark.asyncio
async def test_customer(prepare_container: Callable[[Type[BaseAggregate]], Coroutine[None, None, AggregateContainer]],
                        async_container: AsyncContainer
                        ) -> None:
    model_type: Type[BaseAggregate] = Customer
    domain_container: AggregateContainer = await prepare_container(model_type)
    aggregate: Customer = cast(Customer, domain_container.aggregate)

    service = await async_container.get(CustomerService)

    result: list[CustomerSchemaDefault] = await service.read_by_id([aggregate.entity_id.value])

    assert len(result) == 1
    assert result[0] == CustomerSchemaDefault.create(to_dto(aggregate))
