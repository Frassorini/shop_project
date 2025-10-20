from typing import Callable, Coroutine, Type, cast
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, query
from sqlalchemy.sql import delete, insert, select, update

from shop_project.application.dto.mapper import to_dto
from shop_project.domain import customer
from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.customer import Customer
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.store_item import StoreItem
from shop_project.exceptions import QueryPlanException, UnitOfWorkException
from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.database.models.customer import Customer as CustomerORM
from shop_project.infrastructure.query.domain_load_query import DomainLoadQuery, QueryLock
from shop_project.infrastructure.query.query_builder import QueryPlanBuilder
from shop_project.infrastructure.query.query_criteria import QueryCriteria
from shop_project.infrastructure.query.query_plan import (
    LockQueryPlan,
    NoLockQueryPlan,
    QueryPlan,
)
from shop_project.infrastructure.query.value_container import ValueContainer
from shop_project.infrastructure.query.value_extractor import ValueExtractor
from shop_project.infrastructure.repositories.base_repository import BaseRepository
from shop_project.infrastructure.repositories.customer_repository import (
    CustomerRepository,
)
from shop_project.shared.entity_id import EntityId
from shop_project.infrastructure.resource_manager.resource_container import ResourceContainer


def get_customers() -> list[Customer]:
    return [
        Customer(entity_id=EntityId(uuid4()), name='user_1'),
        Customer(entity_id=EntityId(uuid4()), name='user_2'),
        Customer(entity_id=EntityId(uuid4()), name='user_3'),
        Customer(entity_id=EntityId(uuid4()), name='user_4'),
    ]


@pytest.mark.asyncio
async def test_repository_generic_read(test_db: Database,
                                       fill_database: Callable[[Database, dict[Type[BaseAggregate], list[BaseAggregate]]], Coroutine[None, None, Database]]) -> None:
    async with test_db.get_session() as session:
        customers = get_customers()
        await fill_database(test_db, {Customer: cast(list[BaseAggregate], get_customers())})
        repository = CustomerRepository(session)

        query = QueryPlanBuilder(mutating=False).load(Customer).no_lock().build()
        result = await repository.load(query.queries[0])
        assert len(result) == 4


@pytest.mark.asyncio
async def test_from_id(test_db: Database,
                       fill_database: Callable[[Database, dict[Type[BaseAggregate], list[BaseAggregate]]], Coroutine[None, None, Database]]) -> None:
    uuid_id = uuid4()
    customer = Customer(entity_id=EntityId(uuid_id), name='user_1')

    await fill_database(test_db, {Customer: cast(list[BaseAggregate], [customer])})
    async with test_db.get_session() as session:
        repository = CustomerRepository(session)

        query = (QueryPlanBuilder(mutating=False)
                 .load(Customer)
                 .from_id([uuid_id])
                 .no_lock()
                 .build())
        result = (await repository.load(query.queries[0]))[0]
    
    assert customer == result


@pytest.mark.asyncio
async def test_from_attribute(test_db: Database,
                              fill_database: Callable[[Database, dict[Type[BaseAggregate], list[BaseAggregate]]], Coroutine[None, None, Database]]) -> None:
    customers = get_customers()
    customers_filtered = [customer for customer in customers if customer.name in ['user_1', 'user_2']]
    await fill_database(test_db, {Customer: cast(list[BaseAggregate], customers)})
    async with test_db.get_session() as session:
        repository = CustomerRepository(session)

        query = (
            QueryPlanBuilder(mutating=False)
            .load(Customer)
            .from_attribute("name", ["user_1", "user_2"])
            .no_lock()
            ).build()

        result = (await repository.load(query.queries[0]))
    
    assert customers_filtered[0] in result
    assert customers_filtered[1] in result


# TODO: сравнение числовых значений
@pytest.mark.asyncio
async def xtest_greater_than(test_db: Database,
                            fill_database: Callable[[Database, dict[Type[BaseAggregate], list[BaseAggregate]]], Coroutine[None, None, Database]]) -> None:
    customers = get_customers()
    await fill_database(test_db, {Customer: cast(list[BaseAggregate], customers)})
    async with test_db.get_session() as session:
        repository = CustomerRepository(session)
        customers_filtered = [customer for customer in customers if customer.name > 'user_1']

        query = (
            QueryPlanBuilder(mutating=False)
            .load(Customer)
            .greater_than("name", 'user_1')
            .no_lock()
            ).build()

        result = await repository.load(query.queries[0])
    
    assert customers_filtered == result
    

@pytest.mark.asyncio
async def test_repository_generic_create(test_db: Database,
                                         fill_database: Callable[[Database, dict[Type[BaseAggregate], list[BaseAggregate]]], Coroutine[None, None, Database]]) -> None:
    async with test_db.get_session() as session:
        await fill_database(test_db, {Customer: cast(list[BaseAggregate], get_customers())})
        repository = CustomerRepository(session)
        uuid_id = uuid4()

        resources = ResourceContainer()
        resources.take_snapshot()
        resources.put(Customer, Customer(entity_id=EntityId(uuid_id), name='Bear Lover'))
        resources.take_snapshot()
        await repository.save(resources.get_resource_changes()[Customer])

        query = QueryPlanBuilder(mutating=False).load(Customer).from_id([uuid_id]).no_lock().build()
        result = await repository.load(query.queries[0])
    assert result
