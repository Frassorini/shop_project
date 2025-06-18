from typing import Any, Callable

import pytest
from application.resource_loader.attribute_container import AttributeContainer
from application.resource_loader.attribute_extractor import AttributeExtractor
from application.resource_loader.query_plan import QueryPlan
from application.resource_loader.load_query import LoadQuery
from domain.customer_order.model import CustomerOrder
from domain.store_item.model import StoreItem
from shared.entity_id import EntityId


def test_empty_source():
    with pytest.raises(ValueError):
        query_built: list[LoadQuery[Any, Any]] = QueryPlan().load(CustomerOrder).build()


def test_empty():
    with pytest.raises(ValueError):
        query_built: list[LoadQuery[Any, Any]] = QueryPlan().build()


def test_load_from_attribute():
    query = LoadQuery(CustomerOrder, AttributeContainer[EntityId]('entity_id', [EntityId(1)]))
    
    query_built: list[LoadQuery[Any, Any]] = QueryPlan().load(CustomerOrder).from_attribute("entity_id", [EntityId(1)]).build()
    
    assert query_built[0].attribute_provider.get() == query.attribute_provider.get()
    assert query_built[0].model_type == query.model_type


def test_load_from_id():
    query = LoadQuery(CustomerOrder, AttributeContainer[EntityId]('entity_id', [EntityId(1)]))
    
    query_built: list[LoadQuery[Any, Any]] = QueryPlan().load(CustomerOrder).from_id([EntityId(1)]).build()
    
    assert query_built[0].attribute_provider.get() == query.attribute_provider.get()
    assert query_built[0].model_type == query.model_type


def test_load_from_previous(customer_order_factory: Callable[[], CustomerOrder]):
    customer_order = customer_order_factory()
    
    query = LoadQuery(CustomerOrder, AttributeContainer[EntityId]('entity_id', [EntityId(1)]))
    query.result = [customer_order]
    query.is_loaded = True
    query_store_item = LoadQuery(StoreItem, AttributeExtractor[CustomerOrder, EntityId](query, 'entity_id', lambda x: [item.store_item_id for item in x.get_items()]))
    
    query_plan = QueryPlan().load(StoreItem)
    query_plan.queries.append(query)
    query_built: list[LoadQuery[Any, Any]] = query_plan.from_previous().build()
    
    assert query_built[1].attribute_provider.get() == query_store_item.attribute_provider.get()
    assert query_built[1].model_type == query_store_item.model_type