from typing import Callable

import pytest
from domain.customer import Customer
from domain.store import Store
from infrastructure.exceptions import QueryPlanException, UnitOfWorkException
from infrastructure.query.attribute_container import AttributeContainer
from infrastructure.query.attribute_extractor import AttributeExtractor
from infrastructure.query.query_builder import QueryPlanBuilder
from infrastructure.query.query_plan import LockingQueryPlan, NoLockQueryPlan, QueryPlan
from infrastructure.query.load_query import LoadQuery, QueryLock
from domain.customer_order import CustomerOrder
from domain.store_item import StoreItem
from shared.entity_id import EntityId


def test_empty_source():
    with pytest.raises(QueryPlanException):
        QueryPlanBuilder(mutating=False).load(CustomerOrder).build()


def test_empty():
    with pytest.raises(QueryPlanException):
        QueryPlanBuilder(mutating=False).build()


def test_load_from_attribute():
    query = LoadQuery(CustomerOrder,
                      AttributeContainer('entity_id', 
                                         [EntityId('1')]), 
                      QueryLock.NO_LOCK)
    
    query_built: QueryPlan = (
        QueryPlanBuilder(mutating=False)
        .load(CustomerOrder)
        .from_attribute("entity_id", [EntityId('1')])
        .no_lock()
        .build())
    
    assert query_built.queries[0].attribute_provider.get() == query.attribute_provider.get()
    assert query_built.queries[0].model_type == query.model_type


def test_load_from_id():
    query = LoadQuery(CustomerOrder, 
                      AttributeContainer('entity_id', 
                                         [EntityId('1')]), 
                      QueryLock.NO_LOCK)
    
    query_built: QueryPlan = (
        QueryPlanBuilder(mutating=False)
        .load(CustomerOrder)
        .from_id([EntityId('1')])
        .no_lock()
        .build())
    
    assert query_built.queries[0].attribute_provider.get() == query.attribute_provider.get()
    assert query_built.queries[0].model_type == query.model_type


def test_load_from_previous(customer_order_factory: Callable[[], CustomerOrder]):
    customer_order = customer_order_factory()
    
    query = LoadQuery(CustomerOrder, 
                      AttributeContainer('entity_id', 
                                         [EntityId('1')]), 
                      QueryLock.NO_LOCK)
    query.result = [customer_order]
    query.is_loaded = True
    query_store_item = LoadQuery(StoreItem, 
                                 AttributeExtractor(query, 'entity_id', 
                                                    lambda x: [item.store_item_id for item in x.get_items()]),
                                 QueryLock.NO_LOCK)

    query_builder = QueryPlanBuilder(mutating=False).load(StoreItem)
    query_builder.query_plan.queries.append(query)
    query_built: QueryPlan = query_builder.from_previous().no_lock().build()

    assert query_built.queries[1].attribute_provider.get() == query_store_item.attribute_provider.get()
    assert query_built.queries[1].model_type == query_store_item.model_type


def test_lock_violation():
    with pytest.raises(QueryPlanException):
        QueryPlanBuilder(mutating=True).load(CustomerOrder).from_id([EntityId('1')]).no_lock().build()

    with pytest.raises(QueryPlanException):
        QueryPlanBuilder(mutating=False).load(CustomerOrder).from_id([EntityId('1')]).for_update().build()


def test_correct_locking_load_order():
    plan: QueryPlan = (
        QueryPlanBuilder(mutating=True)
        .load(Customer).from_id([EntityId('1')]).for_share()
        .load(CustomerOrder).from_previous().for_share()
        .load(Store).from_previous().for_share()
        .load(StoreItem).from_previous(1).for_update()
        .build()
    )
    

def test_wrong_locking_load_order():
    with pytest.raises(QueryPlanException):
        plan: QueryPlan = (
            QueryPlanBuilder(mutating=True)
            .load(Customer).from_id([EntityId('1')]).for_share()
            .load(CustomerOrder).from_previous().for_share()
            .load(StoreItem).from_previous().for_update()
            .load(Store).from_previous(1).for_share()
            .build()
        )