import copy
from domain.customer_order_item import CustomerOrderItem, CustomerOrderItemState
from domain.store_item import StoreItem
from domain.cart_item import CartItem
from domain.exceptions import DomainException, NegativeAmountException, StateException
import pytest


def test_order_item(potatoes_store_item_10: StoreItem) -> None:
    cart_item = CartItem(potatoes_store_item_10, 5)

    order_item = CustomerOrderItem(cart_item.store_item, cart_item.amount)

    assert order_item.name == 'potatoes'
    assert order_item.amount == 5
    assert order_item.price == 5 * 1
    assert order_item.store == 'Moscow'


def test_order_item_reserve_fixed_price(potatoes_store_item_10: StoreItem) -> None:
    cart_item = CartItem(potatoes_store_item_10, 5)

    order_item = CustomerOrderItem(cart_item.store_item, cart_item.amount)
    order_item.reserve()
    
    potatoes_store_item_10.price = 10

    assert order_item.name == 'potatoes'
    assert order_item.amount == 5
    assert order_item.price == 5 * 1


def test_order_item_has_parent_store_item(potatoes_store_item_10: StoreItem) -> None:
    potatoes_store_item_10.id_ = 1
    cart_item = CartItem(potatoes_store_item_10, 5)

    order_item = CustomerOrderItem(cart_item.store_item, cart_item.amount)
    
    assert cart_item.store_item == potatoes_store_item_10


def test_create_negative_amount_order_item(potatoes_store_item_10: StoreItem) -> None:
    with pytest.raises(NegativeAmountException):
        order_item = CustomerOrderItem(potatoes_store_item_10, -1)


def test_is_chunk_of(potatoes_store_item_10: StoreItem) -> None:
    potatoes_store_item_10.id_ = 1
    order_item = CustomerOrderItem(potatoes_store_item_10, 5)
    
    assert order_item.is_chunk_of(potatoes_store_item_10)


def test_eq(potatoes_store_item_10: StoreItem) -> None:
    potatoes_store_item_10.id_ = 1
    
    order_item = CustomerOrderItem(potatoes_store_item_10, 5)
    order_item.id_ = 1
    same_order_item = CustomerOrderItem(potatoes_store_item_10, 5)
    same_order_item.id_ = 1
    
    assert order_item == same_order_item


def test_not_eq(potatoes_store_item_10: StoreItem) -> None:
    potatoes_store_item_10.id_ = 1
    
    order_item = CustomerOrderItem(potatoes_store_item_10, 5)
    order_item.id_ = 1
    same_order_item = CustomerOrderItem(potatoes_store_item_10, 5)
    same_order_item.id_ = 2
    
    assert order_item != same_order_item


def test_reserve_item(potatoes_store_item_10: StoreItem) -> None:
    order_item = CustomerOrderItem(potatoes_store_item_10, 10)
    
    order_item.reserve()
    
    assert potatoes_store_item_10.amount == 0


def test_cancel(potatoes_store_item_10: StoreItem) -> None:
    order_item = CustomerOrderItem(potatoes_store_item_10, 10)
    order_item.reserve()
    
    order_item.cancel()
    
    assert potatoes_store_item_10.amount == 10


def test_insufficient_amount(potatoes_store_item_10: StoreItem) -> None:
    order_item = CustomerOrderItem(potatoes_store_item_10, 11)
    
    with pytest.raises(DomainException):
        order_item.reserve()

    assert potatoes_store_item_10.amount == 10


def test_transitions_reserve(potatoes_store_item_10: StoreItem) -> None:
    item = CustomerOrderItem(potatoes_store_item_10, 10)
    
    item.reserve()
    assert item.state == CustomerOrderItemState.RESERVED
    
    item.finalize()
    with pytest.raises(StateException):
        item.reserve()


def test_transitions_finalize(potatoes_store_item_10: StoreItem) -> None:
    item = CustomerOrderItem(potatoes_store_item_10, 10)
    
    with pytest.raises(StateException):
        item.finalize()
    
    item.reserve()
    
    item.finalize()
    assert item.state == CustomerOrderItemState.FINALIZED


def test_transitions_cancel(potatoes_store_item_10: StoreItem) -> None:
    item = CustomerOrderItem(potatoes_store_item_10, 10)
    
    with pytest.raises(StateException):
        item.cancel()
    
    item.reserve()
    item.cancel()
    assert item.state == CustomerOrderItemState.FINALIZED
    
    with pytest.raises(StateException):
        item.cancel()
    
    with pytest.raises(StateException):
        item.finalize()
        
    