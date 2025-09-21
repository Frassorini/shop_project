from typing import Any, Callable, Coroutine, Literal, Type, TypeVar, cast
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.customer import Customer
from shop_project.domain.customer_order import CustomerOrder
from shop_project.domain.store import Store
from shop_project.domain.supplier_order import SupplierOrder
from shop_project.domain.cart import Cart
from shop_project.domain.store_item import StoreItem

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.query.query_builder import QueryPlanBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWork
from shop_project.exceptions import UnitOfWorkException, ResourcesException

from shop_project.infrastructure.query.queries.prebuilt_queries import (
    CountStoreItemsQuery,
    BiggestCustomerOrdersQuery,
)


DomainObject = TypeVar('DomainObject', bound=BaseAggregate)


@pytest.mark.asyncio
async def test_count_store_items(store_item_factory: Callable[..., StoreItem],
                                 store_factory_with_cache: Callable[[str], Store],
                                 test_db: Database,
                                 uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                                 fill_database: Callable[[Database, dict[Type[BaseAggregate], list[BaseAggregate]]], Coroutine[None, None, Database]],
                                 ) -> None:
    model_type: Type[BaseAggregate] = StoreItem
    
    store_items: list[StoreItem] = [
        store_item_factory(name='sausages_1', amount=1, store='Moscow', price="1.0"),
        store_item_factory(name='sausages_2', amount=4, store='Moscow', price="1.0"),
        store_item_factory(name='sausages_3', amount=2, store='Moscow', price="1.0"),
        store_item_factory(name='sausages_4', amount=3, store='Moscow', price="1.0"),
    ]
    
    await fill_database(test_db, {StoreItem: cast(list[BaseAggregate], store_items), Store: cast(list[BaseAggregate], [store_factory_with_cache('Moscow')])})
    uow: UnitOfWork = uow_factory(test_db.get_session(), 'read_only')
    
    query = CountStoreItemsQuery(lock="NO_LOCK")
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=False).add_prebuilt(query)
        )
    
    async with uow:
        pass
    
    assert query.get_result()[0] == 4
