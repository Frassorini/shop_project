from decimal import Decimal
from typing import Callable
from shop_project.domain.purchase_active import PurchaseActive, PurchaseActiveItem
from shop_project.domain.exceptions import DomainException
from shop_project.domain.store_item import StoreItem
import pytest


# def test_snapshot(customer_order_factory: Callable[[], PurchaseActive],
#                   potatoes_store_item_10: Callable[[], StoreItem]) -> None:
#     order = customer_order_factory()
#     store_item: StoreItem = potatoes_store_item_10()
#     order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2)
    
#     snapshot = order.to_dict()
    
#     assert snapshot['entity_id'] == order.entity_id.value
#     assert snapshot['state'] == order.state.value
#     assert snapshot['items'][0]['store_item_id'] == order.get_items()[0].store_item_id.value


# def test_from_snapshot(customer_order_factory: Callable[[], PurchaseActive], 
#                        potatoes_store_item_10: Callable[[], StoreItem]) -> None:
#     order = customer_order_factory()
#     store_item: StoreItem = potatoes_store_item_10()
#     order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2)
    
#     order_from_snapshot = PurchaseActive.from_dict(order.to_dict())
    
#     assert order_from_snapshot.entity_id == order.entity_id
#     assert order_from_snapshot.state == order.state
#     assert order_from_snapshot.get_items() == order.get_items()


# def test_get_item(customer_order_factory: Callable[[], PurchaseActive],
#                   potatoes_store_item_10: Callable[[], StoreItem]) -> None:
#     store_item: StoreItem = potatoes_store_item_10()
#     order = customer_order_factory()
    
#     order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2)
    
#     order_item: PurchaseActiveItem = order.get_item(store_item.entity_id)
    
#     assert order_item.amount == 2

