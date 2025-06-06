from typing import Callable

import pytest
from domain.exceptions import DomainException
from domain.store_item.model import StoreItem
from domain.cart import Cart, CartItem



def test_add_item(cart_factory: Callable[[], Cart],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = cart_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    
    order.add_item(store_item_id=store_item.entity_id, amount=2, store=store_item.store)


def test_add_negative_amount(cart_factory: Callable[[], Cart],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = cart_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, amount=-2, store=store_item.store)


def test_get_item(cart_factory: Callable[[], Cart],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = cart_factory()
    
    order.add_item(store_item_id=store_item.entity_id, amount=2, store=store_item.store)
    
    order_item: CartItem = order.get_item(store_item.entity_id)
    
    assert order_item.amount == 2


def test_cannot_add_duplicate_item(cart_factory: Callable[[], Cart], 
                                   potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = cart_factory()
    
    order.add_item(store_item_id=store_item.entity_id, amount=2, store=store_item.store)
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, amount=3, store=store_item.store)


def test_cannot_add_from_another_store(cart_factory: Callable[[], Cart], 
                                       potatoes_store_item_10: Callable[..., StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10(store="Petersburg")
    order = cart_factory()
    
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, amount=2, store=store_item.store)
    