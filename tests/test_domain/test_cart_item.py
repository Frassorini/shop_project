import copy
from typing import Callable
from domain.entity_id import EntityId
from domain.store_item import StoreItem
from domain.cart_item import CartItem
from domain.exceptions import DomainException, NegativeAmountException
import pytest


def test_cart_item(unique_id_factory: Callable[[], EntityId], potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item = potatoes_store_item_10
    
    cart_item = CartItem(unique_id_factory(), store_item=store_item(), amount=3)
    
    assert cart_item.name == 'potatoes'
    assert cart_item.amount == 3


def test_cart_item_has_parent_store_item(unique_id_factory: Callable[[], EntityId], potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item = potatoes_store_item_10()
    
    cart_item = CartItem(unique_id_factory(), store_item=store_item, amount=3)
    
    assert cart_item.store_item is store_item


def test_create_negative_amount_cart_item(unique_id_factory: Callable[[], EntityId], potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item = potatoes_store_item_10
    with pytest.raises(NegativeAmountException):
        cart_item = CartItem(unique_id_factory(), store_item(), amount=-1)


def test_negative_amount_cart_item(unique_id_factory: Callable[[], EntityId], potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item = potatoes_store_item_10
    with pytest.raises(NegativeAmountException):
        cart_item = CartItem(unique_id_factory(), store_item(), amount=1)
        cart_item.amount -= 5


def test_cart_item_price(unique_id_factory: Callable[[], EntityId], potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item = potatoes_store_item_10()
    cart_item = CartItem(unique_id_factory(),  store_item=store_item, amount=2)
    
    assert cart_item.price == store_item.price * 2


def test_is_chunk_of(unique_id_factory: Callable[[], EntityId], potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item = potatoes_store_item_10()
    cart_item = CartItem(unique_id_factory(), store_item=store_item, amount=5)
    
    assert cart_item.is_chunk_of(store_item)


def test_eq(potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item = potatoes_store_item_10()
    potatoes_cart = CartItem(EntityId(1), store_item=store_item, amount=5)
    other_potatoes_cart = CartItem(EntityId(1), store_item=store_item, amount=5)
    
    assert potatoes_cart == other_potatoes_cart


def test_not_eq(potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item = potatoes_store_item_10()
    potatoes_cart = CartItem(EntityId(1), store_item=store_item, amount=5)
    other_potatoes_cart = CartItem(EntityId(2), store_item=store_item, amount=5)
    
    assert potatoes_cart != other_potatoes_cart