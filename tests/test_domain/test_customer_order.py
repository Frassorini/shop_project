from decimal import Decimal
from typing import Callable
from shop_project.domain.customer_order import CustomerOrder, CustomerOrderState, CustomerOrderItem
from shop_project.domain.exceptions import DomainException
from shop_project.domain.store_item import StoreItem
import pytest


def test_snapshot(customer_order_factory: Callable[[], CustomerOrder],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    snapshot = order.to_dict()
    
    assert snapshot['entity_id'] == order.entity_id.value
    assert snapshot['state'] == order.state.value
    assert snapshot['items'][0]['store_item_id'] == order.get_items()[0].store_item_id.value


def test_from_snapshot(customer_order_factory: Callable[[], CustomerOrder], 
                       potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    order_from_snapshot = CustomerOrder.from_dict(order.to_dict())
    
    assert order_from_snapshot.entity_id == order.entity_id
    assert order_from_snapshot.state == order.state
    assert order_from_snapshot.get_items() == order.get_items()
    

def test_add_item(customer_order_factory: Callable[[], CustomerOrder],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)


def test_add_negative_amount(customer_order_factory: Callable[[], CustomerOrder],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=-2, store_id=store_item.store_id)


def test_add_negative_price(customer_order_factory: Callable[[], CustomerOrder],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, price=Decimal(-1), amount=2, store_id=store_item.store_id)


def test_get_item(customer_order_factory: Callable[[], CustomerOrder],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    order_item: CustomerOrderItem = order.get_item(store_item.entity_id)
    
    assert order_item.amount == 2


def test_cannot_add_duplicate_item(customer_order_factory: Callable[[], CustomerOrder], 
                                   potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=3, store_id=store_item.store_id)


def test_cannot_add_from_another_store(customer_order_factory: Callable[[], CustomerOrder], 
                                       potatoes_store_item_10: Callable[..., StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10(store="Petersburg")
    order = customer_order_factory()
    
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)


@pytest.mark.parametrize("from_state, method", [
    (CustomerOrderState.PENDING, "reserve"),

    (CustomerOrderState.RESERVED, "pay"),
    
    (CustomerOrderState.PAID, "claim"),
    (CustomerOrderState.PAID, "unclaim"),
    (CustomerOrderState.PAID, "refund"),
    
    (CustomerOrderState.UNCLAIMED, "refund"),
])
def test_valid_transitions(from_state: CustomerOrderState, method: str, 
                           customer_order_factory: Callable[[], CustomerOrder],
                           transition_order_to_state: Callable[[CustomerOrder, CustomerOrderState], None], 
                           potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    transition_order_to_state(order, from_state)
    
    getattr(order, method)()


@pytest.mark.parametrize("from_state, method", [
    (CustomerOrderState.PENDING, "pay"),
    (CustomerOrderState.PENDING, "claim"),
    (CustomerOrderState.PENDING, "unclaim"),
    (CustomerOrderState.PENDING, "refund"),
    (CustomerOrderState.PENDING, "cancel"),
    
    (CustomerOrderState.RESERVED, "reserve"),
    (CustomerOrderState.RESERVED, "claim"),
    (CustomerOrderState.RESERVED, "unclaim"),
    (CustomerOrderState.RESERVED, "refund"),
    
    (CustomerOrderState.PAID, "reserve"),
    (CustomerOrderState.PAID, "pay"),
    (CustomerOrderState.PAID, "cancel"),
    
    (CustomerOrderState.CLAIMED, "reserve"),
    (CustomerOrderState.CLAIMED, "pay"),
    (CustomerOrderState.CLAIMED, "claim"),
    (CustomerOrderState.CLAIMED, "unclaim"),
    (CustomerOrderState.CLAIMED, "refund"),
    (CustomerOrderState.CLAIMED, "cancel"),
    
    (CustomerOrderState.CANCELLED, "reserve"),
    (CustomerOrderState.CANCELLED, "pay"),
    (CustomerOrderState.CANCELLED, "claim"),
    (CustomerOrderState.CANCELLED, "unclaim"),
    (CustomerOrderState.CANCELLED, "refund"),
    (CustomerOrderState.CANCELLED, "cancel"),
])
def test_invalid_transitions(from_state: CustomerOrderState, method: str, 
                             customer_order_factory: Callable[[], CustomerOrder], 
                             transition_order_to_state: Callable[[CustomerOrder, CustomerOrderState], None], 
                             potatoes_store_item_10: Callable[[], StoreItem],) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    transition_order_to_state(order, from_state)
        
    with pytest.raises(DomainException):
        getattr(order, method)()
    

@pytest.mark.parametrize("from_state, method", [
    (CustomerOrderState.PENDING, "can_be_reserved"),

    (CustomerOrderState.RESERVED, "can_be_paid"),
    
    (CustomerOrderState.PAID, "can_be_claimed"),
    (CustomerOrderState.PAID, "can_be_unclaimed"),
    (CustomerOrderState.PAID, "can_be_refunded"),
    
    (CustomerOrderState.UNCLAIMED, "can_be_refunded"),
])
def test_valid_checks(from_state: CustomerOrderState, method: str, 
                      customer_order_factory: Callable[[], CustomerOrder], 
                      transition_order_to_state: Callable[[CustomerOrder, CustomerOrderState], None], 
                      potatoes_store_item_10: Callable[[], StoreItem],) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    transition_order_to_state(order, from_state)
    
    assert getattr(order, method)()


@pytest.mark.parametrize("from_state, method", [
    (CustomerOrderState.PENDING, "can_be_paid"),
    (CustomerOrderState.PENDING, "can_be_claimed"),
    (CustomerOrderState.PENDING, "can_be_cancelled"),
    
    (CustomerOrderState.RESERVED, "can_be_reserved"),
    (CustomerOrderState.RESERVED, "can_be_claimed"),
    
    (CustomerOrderState.PAID, "can_be_reserved"),
    (CustomerOrderState.PAID, "can_be_paid"),
    
    (CustomerOrderState.CLAIMED, "can_be_reserved"),
    (CustomerOrderState.CLAIMED, "can_be_paid"),
    (CustomerOrderState.CLAIMED, "can_be_claimed"),
    (CustomerOrderState.CLAIMED, "can_be_cancelled"),
    
    (CustomerOrderState.CANCELLED, "can_be_reserved"),
    (CustomerOrderState.CANCELLED, "can_be_paid"),
    (CustomerOrderState.CANCELLED, "can_be_claimed"),
    (CustomerOrderState.CANCELLED, "can_be_cancelled"),
])
def test_invalid_checks(from_state: CustomerOrderState, method: str, 
                        customer_order_factory: Callable[[], CustomerOrder],
                        transition_order_to_state: Callable[[CustomerOrder, CustomerOrderState], None], 
                        potatoes_store_item_10: Callable[[], StoreItem],) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    transition_order_to_state(order, from_state)
        
    assert not getattr(order, method)()