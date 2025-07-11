from typing import Callable

import pytest
from domain.customer import Customer
from domain.store import Store
from infrastructure.exceptions import QueryPlanException, UnitOfWorkException
from infrastructure.query.value_container import ValueContainer
from infrastructure.query.value_extractor import ValueExtractor
from infrastructure.query.query_builder import QueryPlanBuilder
from infrastructure.query.query_plan import LockQueryPlan, NoLockQueryPlan, QueryPlan
from infrastructure.query.load_query import LoadQuery, QueryLock
from domain.customer_order import CustomerOrder
from domain.store_item import StoreItem
from infrastructure.query.query_criteria import QueryCriteria
from shared.entity_id import EntityId


def test_empty_source():
    with pytest.raises(QueryPlanException):
        QueryPlanBuilder(mutating=False).load(CustomerOrder).build()


def test_empty():
    with pytest.raises(QueryPlanException):
        QueryPlanBuilder(mutating=False).build()


def test_load_from_attribute():
    query = LoadQuery(CustomerOrder,
                      QueryCriteria().criterion_in("entity_id", ValueContainer([EntityId('1')])), 
                      QueryLock.NO_LOCK)
    
    query_built: QueryPlan = (
        QueryPlanBuilder(mutating=False)
        .load(CustomerOrder)
        .from_attribute("entity_id", [EntityId('1')])
        .no_lock()
        .build())
    
    assert query_built.queries[0].criteria.criteria[0].value_provider.get() == query.criteria.criteria[0].value_provider.get()
    assert query_built.queries[0].model_type == query.model_type


def test_load_from_id():
    query = LoadQuery(CustomerOrder, 
                      QueryCriteria().criterion_in("entity_id", ValueContainer([EntityId('1')])), 
                      QueryLock.NO_LOCK)
    
    query_built: QueryPlan = (
        QueryPlanBuilder(mutating=False)
        .load(CustomerOrder)
        .from_id([EntityId('1')])
        .no_lock()
        .build())
    
    assert query_built.queries[0].criteria.criteria[0].value_provider.get() == query.criteria.criteria[0].value_provider.get()
    assert query_built.queries[0].model_type == query.model_type


def test_load_from_previous(customer_order_factory: Callable[[], CustomerOrder]):
    customer_order = customer_order_factory()
    
    query = LoadQuery(CustomerOrder, 
                      QueryCriteria().criterion_in("entity_id", ValueContainer([EntityId('1')])), 
                      QueryLock.NO_LOCK)
    query.load([customer_order])
    query_store_item = LoadQuery(StoreItem, 
                                 QueryCriteria().criterion_in("entity_id", 
                                 ValueExtractor(query,
                                                    lambda x: [item.store_item_id for item in x.get_items()])
                                 ),
                                 QueryLock.NO_LOCK)

    query_builder = QueryPlanBuilder(mutating=False).load(StoreItem)
    query_builder.query_plan.queries.append(query)
    query_built: QueryPlan = query_builder.from_previous().no_lock().build()

    assert query_built.queries[1].criteria.criteria[0].value_provider.get() == query_store_item.criteria.criteria[0].value_provider.get()
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