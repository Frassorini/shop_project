from typing import Awaitable, Callable, Type, cast
from uuid import uuid4

import pytest

from shop_project.domain.entities.customer import Customer
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.infrastructure.registries.resources_registry import ResourcesRegistry
from shop_project.infrastructure.repositories.customer_repository import (
    CustomerRepository,
)
from shop_project.infrastructure.resource_manager.resource_container import (
    ResourceContainer,
)


def get_customers() -> list[Customer]:
    return [
        Customer(entity_id=uuid4(), name="user_1"),
        Customer(entity_id=uuid4(), name="user_2"),
        Customer(entity_id=uuid4(), name="user_3"),
        Customer(entity_id=uuid4(), name="user_4"),
    ]


@pytest.mark.asyncio
async def test_repository_generic_read(
    test_db: Database,
    fill_database: Callable[
        [dict[Type[PersistableEntity], list[PersistableEntity]]], Awaitable[None]
    ],
) -> None:
    async with test_db.create_session() as session:
        customers = get_customers()
        await fill_database({Customer: cast(list[PersistableEntity], get_customers())})
        repository = CustomerRepository(session)

        query = QueryBuilder(mutating=False).load(Customer).no_lock().build()
        result = await repository.load(query.queries[0])
        assert len(result) == 4


@pytest.mark.asyncio
async def test_from_id(
    test_db: Database,
    fill_database: Callable[
        [dict[Type[PersistableEntity], list[PersistableEntity]]], Awaitable[None]
    ],
) -> None:
    uuid_id = uuid4()
    customer = Customer(entity_id=uuid_id, name="user_1")

    await fill_database({Customer: cast(list[PersistableEntity], [customer])})
    async with test_db.create_session() as session:
        repository = CustomerRepository(session)

        query = (
            QueryBuilder(mutating=False)
            .load(Customer)
            .from_id([uuid_id])
            .no_lock()
            .build()
        )
        result = (await repository.load(query.queries[0]))[0]

    assert customer == result


@pytest.mark.asyncio
async def test_from_attribute(
    test_db: Database,
    fill_database: Callable[
        [dict[Type[PersistableEntity], list[PersistableEntity]]], Awaitable[None]
    ],
) -> None:
    customers = get_customers()
    customers_filtered = [
        customer for customer in customers if customer.name in ["user_1", "user_2"]
    ]
    await fill_database({Customer: cast(list[PersistableEntity], customers)})
    async with test_db.create_session() as session:
        repository = CustomerRepository(session)

        query = (
            QueryBuilder(mutating=False)
            .load(Customer)
            .from_attribute("name", ["user_1", "user_2"])
            .no_lock()
        ).build()

        result = await repository.load(query.queries[0])

    assert customers_filtered[0] in result
    assert customers_filtered[1] in result


# TODO: сравнение числовых значений
@pytest.mark.asyncio
async def xtest_greater_than(
    test_db: Database,
    fill_database: Callable[
        [dict[Type[PersistableEntity], list[PersistableEntity]]], Awaitable[None]
    ],
) -> None:
    customers = get_customers()
    await fill_database({Customer: cast(list[PersistableEntity], customers)})
    async with test_db.create_session() as session:
        repository = CustomerRepository(session)
        customers_filtered = [
            customer for customer in customers if customer.name > "user_1"
        ]

        query = (
            QueryBuilder(mutating=False)
            .load(Customer)
            .greater_than("name", "user_1")
            .no_lock()
        ).build()

        result = await repository.load(query.queries[0])

    assert customers_filtered == result


@pytest.mark.asyncio
async def test_repository_generic_create(
    test_db: Database,
    fill_database: Callable[
        [dict[Type[PersistableEntity], list[PersistableEntity]]], Awaitable[None]
    ],
) -> None:
    async with test_db.create_session() as session:
        await fill_database({Customer: cast(list[PersistableEntity], get_customers())})
        repository = CustomerRepository(session)
        uuid_id = uuid4()

        resources = ResourceContainer(resources_registry=ResourcesRegistry.get_map())
        resources.take_snapshot()
        resources.put(Customer, Customer(entity_id=uuid_id, name="Bear Lover"))
        resources.take_snapshot()
        await repository.save(resources.get_resource_changes()[Customer])

        query = (
            QueryBuilder(mutating=False)
            .load(Customer)
            .from_id([uuid_id])
            .no_lock()
            .build()
        )
        result = await repository.load(query.queries[0])
    assert result
