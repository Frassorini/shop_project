import copy
from decimal import Decimal
from typing import Callable

import pytest

from shop_project.application.dto.purchase_active_dto import PurchaseActiveDTO
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.application.dto.mapper import to_dto, to_domain
from shop_project.domain.store_item import StoreItem

def test_to_dto(customer_order_factory: Callable[[], PurchaseActive], potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    dto = to_dto(order)
    
    assert dto.entity_id == order.entity_id.value
    assert dto.state == order.state.value
    assert dto.items[0].store_item_id == order.get_items()[0].store_item_id.value


def test_to_domain(customer_order_factory: Callable[[], PurchaseActive], potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    dto = to_dto(order)
    order_from_dto = to_domain(dto)
    
    assert order_from_dto.entity_id == order.entity_id
    assert order_from_dto.state == order.state
    assert order_from_dto.get_items() == order.get_items()