from typing import Callable

import pytest
from shop_project.domain.exceptions import DomainException
from shop_project.domain.store_item import StoreItem
from shop_project.domain.cart import Cart, CartItem



def test_add_item(cart_factory: Callable[[], Cart],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    cart = cart_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    
    cart.add_item(store_item_id=store_item.entity_id, amount=2, store_id=store_item.store_id)


def test_add_negative_amount(cart_factory: Callable[[], Cart],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    cart = cart_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    with pytest.raises(DomainException):
        cart.add_item(store_item_id=store_item.entity_id, amount=-2, store_id=store_item.store_id)


def test_get_item(cart_factory: Callable[[], Cart],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    cart = cart_factory()
    
    cart.add_item(store_item_id=store_item.entity_id, amount=2, store_id=store_item.store_id)
    
    cart_item: CartItem = cart.get_item(store_item.entity_id)
    
    assert cart_item.amount == 2


def test_cannot_add_duplicate_item(cart_factory: Callable[[], Cart], 
                                   potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    cart = cart_factory()
    
    cart.add_item(store_item_id=store_item.entity_id, amount=2, store_id=store_item.store_id)
    with pytest.raises(DomainException):
        cart.add_item(store_item_id=store_item.entity_id, amount=3, store_id=store_item.store_id)


def test_cannot_add_from_another_store(cart_factory: Callable[[], Cart], 
                                       potatoes_store_item_10: Callable[..., StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10(store="Petersburg")
    cart = cart_factory()
    
    with pytest.raises(DomainException):
        cart.add_item(store_item_id=store_item.entity_id, amount=2, store_id=store_item.store_id)
    

def test_snapshot(cart_factory: Callable[[], Cart], 
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    cart: Cart = cart_factory()
    
    cart.add_item(store_item_id=store_item.entity_id, amount=2, store_id=store_item.store_id)
    
    snapshot = cart.snapshot()
    
    assert snapshot['items'][0] == {'store_item_id': store_item.entity_id.to_str(), 'amount': '2'}


def test_from_snapshot(cart_factory: Callable[[], Cart], 
                       potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    cart: Cart = cart_factory()
    
    cart.add_item(store_item_id=store_item.entity_id, amount=2, store_id=store_item.store_id)
    
    snapshot = cart.snapshot()
    
    cart_from_snapshot: Cart = Cart.from_snapshot(snapshot)
    
    assert cart_from_snapshot.get_items() == cart.get_items()