from typing import Any, Callable

import pytest
from infrastructure.query.attribute_container import AttributeContainer
from infrastructure.query.attribute_extractor import AttributeExtractor
from infrastructure.query.query_plan import QueryPlan
from infrastructure.query.load_query import LoadQuery
from domain.customer_order import CustomerOrder
from domain.store_item import StoreItem
from shared.entity_id import EntityId


def test_empty_source():
    with pytest.raises(ValueError):
        query_built: list[LoadQuery] = QueryPlan().load(CustomerOrder).build()


def test_empty():
    with pytest.raises(ValueError):
        query_built: list[LoadQuery] = QueryPlan().build()


def test_load_from_attribute():
    query = LoadQuery(CustomerOrder, AttributeContainer('entity_id', [EntityId('1')]))
    
    query_built: list[LoadQuery] = QueryPlan().load(CustomerOrder).from_attribute("entity_id", [EntityId('1')]).build()
    
    assert query_built[0].attribute_provider.get() == query.attribute_provider.get()
    assert query_built[0].model_type == query.model_type


def test_load_from_id():
    query = LoadQuery(CustomerOrder, AttributeContainer('entity_id', [EntityId('1')]))
    
    query_built: list[LoadQuery] = QueryPlan().load(CustomerOrder).from_id([EntityId('1')]).build()
    
    assert query_built[0].attribute_provider.get() == query.attribute_provider.get()
    assert query_built[0].model_type == query.model_type


def test_load_from_previous(customer_order_factory: Callable[[], CustomerOrder]):
    customer_order = customer_order_factory()
    
    query = LoadQuery(CustomerOrder, AttributeContainer('entity_id', [EntityId('1')]))
    query.result = [customer_order]
    query.is_loaded = True
    query_store_item = LoadQuery(StoreItem, AttributeExtractor(query, 'entity_id', lambda x: [item.store_item_id for item in x.get_items()]))
    
    query_plan = QueryPlan().load(StoreItem)
    query_plan.queries.append(query)
    query_built: list[LoadQuery] = query_plan.from_previous().build()
    
    assert query_built[1].attribute_provider.get() == query_store_item.attribute_provider.get()
    assert query_built[1].model_type == query_store_item.model_type