import copy
from domain.store_item import StoreItem
from domain.cart_item import CartItem
from domain.exceptions import DomainException, NegativeAmountException
import pytest


def test_cart_item(potatoes_store_item_10: StoreItem) -> None:
    store_item = potatoes_store_item_10
    
    cart_item = CartItem(store_item=store_item, amount=3)
    
    assert cart_item.name == 'potatoes'
    assert cart_item.amount == 3


def test_cart_item_has_parent_store_item(potatoes_store_item_10: StoreItem) -> None:
    store_item = potatoes_store_item_10
    
    cart_item = CartItem(store_item=store_item, amount=3)
    
    assert cart_item.store_item is store_item


def test_create_negative_amount_cart_item(potatoes_store_item_10: StoreItem) -> None:
    store_item = potatoes_store_item_10
    with pytest.raises(NegativeAmountException):
        cart_item = CartItem(store_item, amount=-1)


def test_negative_amount_cart_item(potatoes_store_item_10: StoreItem) -> None:
    store_item = potatoes_store_item_10
    with pytest.raises(NegativeAmountException):
        cart_item = CartItem(store_item, amount=1)
        cart_item.amount -= 5


def test_cart_item_price(potatoes_store_item_10: StoreItem) -> None:
    cart_item = CartItem(store_item=potatoes_store_item_10, amount=2)
    
    assert cart_item.price == potatoes_store_item_10.price * 2


def test_is_chunk_of(potatoes_store_item_10: StoreItem) -> None:
    potatoes_store_item_10.id_ = 1
    cart_item = CartItem(potatoes_store_item_10, 5)
    
    assert cart_item.is_chunk_of(potatoes_store_item_10)


def test_eq(potatoes_store_item_10: StoreItem) -> None:
    potatoes_store_item_10.id_ = 1
    
    potatoes_cart = CartItem(potatoes_store_item_10, 5)
    potatoes_cart.id_ = 1
    other_potatoes_cart = CartItem(potatoes_store_item_10, 5)
    other_potatoes_cart.id_ = 1
    
    assert potatoes_cart == other_potatoes_cart


def test_not_eq(potatoes_store_item_10: StoreItem) -> None:
    potatoes_store_item_10.id_ = 1
    
    potatoes_cart = CartItem(potatoes_store_item_10, 5)
    potatoes_cart.id_ = 1
    other_potatoes_cart = CartItem(potatoes_store_item_10, 5)
    other_potatoes_cart.id_ = 2
    
    assert potatoes_cart != other_potatoes_cart