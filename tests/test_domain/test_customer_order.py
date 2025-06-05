from typing import Callable
from domain.customer import Customer
from domain.customer_order import CustomerOrder, CustomerOrderState, CustomerOrderItem
from domain.exceptions import DomainException
from domain.store_item import StoreItem
import pytest
    

def test_add_item(customer_order_factory: Callable[[], CustomerOrder],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store=store_item.store)


def test_add_negative_amount(customer_order_factory: Callable[[], CustomerOrder],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=-2, store=store_item.store)


def test_add_negative_price(customer_order_factory: Callable[[], CustomerOrder],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, price=-1, amount=2, store=store_item.store)


def test_get_item(customer_order_factory: Callable[[], CustomerOrder],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store=store_item.store)
    
    order_item: CustomerOrderItem = order.get_item(store_item.entity_id)
    
    assert order_item.amount == 2


def test_cannot_add_duplicate_item(customer_order_factory: Callable[[], CustomerOrder], 
                                   potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store=store_item.store)
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=3, store=store_item.store)


def test_cannot_add_from_another_store(customer_order_factory: Callable[[], CustomerOrder], 
                                       potatoes_store_item_10: Callable[..., StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10(store="Petersburg")
    order = customer_order_factory()
    
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store=store_item.store)
    

def test_valid_transitions(customer_order_factory: Callable[[], CustomerOrder], 
                           potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store=store_item.store)
    
    order.reserve()
    
    order.pay()
    
    order.receive()


@pytest.mark.parametrize("from_state, method", [
    (CustomerOrderState.PENDING, "pay"),
    (CustomerOrderState.PENDING, "receive"),
    (CustomerOrderState.PENDING, "cancel"),
    
    (CustomerOrderState.RESERVED, "reserve"),
    (CustomerOrderState.RESERVED, "receive"),
    
    (CustomerOrderState.PAID, "reserve"),
    (CustomerOrderState.PAID, "pay"),
    
    (CustomerOrderState.RECEIVED, "reserve"),
    (CustomerOrderState.RECEIVED, "pay"),
    (CustomerOrderState.RECEIVED, "receive"),
    (CustomerOrderState.RECEIVED, "cancel"),
    
    (CustomerOrderState.CANCELLED, "reserve"),
    (CustomerOrderState.CANCELLED, "pay"),
    (CustomerOrderState.CANCELLED, "receive"),
    (CustomerOrderState.CANCELLED, "cancel"),
])
def test_invalid_transitions(from_state: CustomerOrderState, method: str, 
                             customer_order_factory: Callable[[], CustomerOrder], 
                             potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store=store_item.store)
    
    match from_state:
        case CustomerOrderState.PENDING:
            pass
        case CustomerOrderState.RESERVED:
            order.reserve()
        case CustomerOrderState.PAID:
            order.reserve()
            order.pay()
        case CustomerOrderState.RECEIVED:
            order.reserve()
            order.pay()
            order.receive()
        case CustomerOrderState.CANCELLED:
            order.reserve()
            order.cancel()
        
    with pytest.raises(DomainException):
        getattr(order, method)()
    

def test_valid_checks(customer_order_factory: Callable[[], CustomerOrder], 
                      potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store=store_item.store)
    
    assert order.can_be_reserved()
    assert not order.can_be_cancelled()
    order.reserve()
    
    assert order.can_be_paid()
    assert order.can_be_cancelled()
    order.pay()
    
    assert order.can_be_received()
    assert order.can_be_cancelled()
    order.receive()


@pytest.mark.parametrize("from_state, method", [
    (CustomerOrderState.PENDING, "can_be_paid"),
    (CustomerOrderState.PENDING, "can_be_received"),
    (CustomerOrderState.PENDING, "can_be_cancelled"),
    
    (CustomerOrderState.RESERVED, "can_be_reserved"),
    (CustomerOrderState.RESERVED, "can_be_received"),
    
    (CustomerOrderState.PAID, "can_be_reserved"),
    (CustomerOrderState.PAID, "can_be_paid"),
    
    (CustomerOrderState.RECEIVED, "can_be_reserved"),
    (CustomerOrderState.RECEIVED, "can_be_paid"),
    (CustomerOrderState.RECEIVED, "can_be_received"),
    (CustomerOrderState.RECEIVED, "can_be_cancelled"),
    
    (CustomerOrderState.CANCELLED, "can_be_reserved"),
    (CustomerOrderState.CANCELLED, "can_be_paid"),
    (CustomerOrderState.CANCELLED, "can_be_received"),
    (CustomerOrderState.CANCELLED, "can_be_cancelled"),
])
def test_invalid_checks(from_state: CustomerOrderState, method: str, 
                        customer_order_factory: Callable[[], CustomerOrder], 
                        potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store=store_item.store)
    
    match from_state:
        case CustomerOrderState.PENDING:
            pass
        case CustomerOrderState.RESERVED:
            order.reserve()
        case CustomerOrderState.PAID:
            order.reserve()
            order.pay()
        case CustomerOrderState.RECEIVED:
            order.reserve()
            order.pay()
            order.receive()
        case CustomerOrderState.CANCELLED:
            order.reserve()
            order.cancel()
        
    assert not getattr(order, method)()