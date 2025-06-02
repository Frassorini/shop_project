import copy
from typing import Callable
from domain.customer_order_item import CustomerOrderItem, CustomerOrderItemState
from domain.entity_id import EntityId
from domain.store_item import StoreItem
from domain.cart_item import CartItem
from domain.exceptions import DomainException, NegativeAmountException, StateException
import pytest


def test_order_item(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    cart_item = CartItem(unique_id_factory(), store_item=store_item, amount=5)

    order_item = CustomerOrderItem(unique_id_factory(), store_item=cart_item.store_item, amount=cart_item.amount)

    assert order_item.name == 'potatoes'
    assert order_item.amount == 5
    assert order_item.price == 5 * 1
    assert order_item.store == 'Moscow'


def test_order_item_reserve_fixed_price(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    cart_item = CartItem(unique_id_factory(), store_item=store_item, amount=5)

    order_item = CustomerOrderItem(unique_id_factory(), store_item=cart_item.store_item, amount=cart_item.amount)
    order_item.reserve()
    
    store_item.price = 10

    assert order_item.name == 'potatoes'
    assert order_item.amount == 5
    assert order_item.price == 5 * 1


def test_order_item_has_parent_store_item(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    cart_item = CartItem(unique_id_factory(), store_item=store_item, amount=5)

    order_item = CustomerOrderItem(unique_id_factory(), store_item=cart_item.store_item, amount=cart_item.amount)
    
    assert order_item.store_item == store_item


def test_create_negative_amount_order_item(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    with pytest.raises(NegativeAmountException):
        order_item = CustomerOrderItem(unique_id_factory(), store_item=store_item, amount=-1)


def test_is_chunk_of(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    order_item = CustomerOrderItem(unique_id_factory(), store_item=store_item, amount=5)
    
    assert order_item.is_chunk_of(store_item)


def test_eq(
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    
    order_item = CustomerOrderItem(EntityId(1), store_item=store_item, amount=5)
    same_order_item = CustomerOrderItem(EntityId(1), store_item=store_item, amount=5)
    
    assert order_item == same_order_item


def test_not_eq(
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    
    order_item = CustomerOrderItem(EntityId(1), store_item=store_item, amount=5)
    same_order_item = CustomerOrderItem(EntityId(2), store_item=store_item, amount=5)
    
    assert order_item != same_order_item


def test_reserve_item(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    order_item = CustomerOrderItem(unique_id_factory(), store_item=store_item, amount=10)
    
    order_item.reserve()
    
    assert store_item.amount == 0


def test_cancel(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    order_item = CustomerOrderItem(unique_id_factory(), store_item=store_item, amount=10)
    order_item.reserve()
    
    order_item.cancel()
    
    assert store_item.amount == 10


def test_insufficient_amount(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    order_item = CustomerOrderItem(unique_id_factory(), store_item=store_item, amount=11)
    
    with pytest.raises(DomainException):
        order_item.reserve()

    assert store_item.amount == 10


def test_transitions_reserve(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    item = CustomerOrderItem(unique_id_factory(), store_item=store_item, amount=10)
    
    item.reserve()
    assert item.state == CustomerOrderItemState.RESERVED
    
    item.finalize()
    with pytest.raises(StateException):
        item.reserve()


def test_transitions_finalize(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    item = CustomerOrderItem(unique_id_factory(), store_item=store_item, amount=10)
    
    with pytest.raises(StateException):
        item.finalize()
    
    item.reserve()
    
    item.finalize()
    assert item.state == CustomerOrderItemState.FINALIZED


def test_transitions_cancel(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    item = CustomerOrderItem(unique_id_factory(), store_item=store_item, amount=10)
    
    with pytest.raises(StateException):
        item.cancel()
    
    item.reserve()
    item.cancel()
    assert item.state == CustomerOrderItemState.FINALIZED
    
    with pytest.raises(StateException):
        item.cancel()
    
    with pytest.raises(StateException):
        item.finalize()