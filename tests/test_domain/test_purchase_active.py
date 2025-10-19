from decimal import Decimal
from typing import Callable
from shop_project.domain.purchase_active import PurchaseActive, PurchaseActiveState, PurchaseActiveItem
from shop_project.domain.exceptions import DomainException
from shop_project.domain.store_item import StoreItem
import pytest


def test_snapshot(customer_order_factory: Callable[[], PurchaseActive],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    snapshot = order.to_dict()
    
    assert snapshot['entity_id'] == order.entity_id.value
    assert snapshot['state'] == order.state.value
    assert snapshot['items'][0]['store_item_id'] == order.get_items()[0].store_item_id.value


def test_from_snapshot(customer_order_factory: Callable[[], PurchaseActive], 
                       potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    order_from_snapshot = PurchaseActive.from_dict(order.to_dict())
    
    assert order_from_snapshot.entity_id == order.entity_id
    assert order_from_snapshot.state == order.state
    assert order_from_snapshot.get_items() == order.get_items()
    

def test_add_item(customer_order_factory: Callable[[], PurchaseActive],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)


def test_add_negative_amount(customer_order_factory: Callable[[], PurchaseActive],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=-2, store_id=store_item.store_id)


def test_add_negative_price(customer_order_factory: Callable[[], PurchaseActive],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    order = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, price=Decimal(-1), amount=2, store_id=store_item.store_id)


def test_get_item(customer_order_factory: Callable[[], PurchaseActive],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    order_item: PurchaseActiveItem = order.get_item(store_item.entity_id)
    
    assert order_item.amount == 2


def test_cannot_add_duplicate_item(customer_order_factory: Callable[[], PurchaseActive], 
                                   potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=3, store_id=store_item.store_id)


def test_cannot_add_from_another_store(customer_order_factory: Callable[[], PurchaseActive], 
                                       potatoes_store_item_10: Callable[..., StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10(store="Petersburg")
    order = customer_order_factory()
    
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)


@pytest.mark.parametrize("from_state, method", [
    (PurchaseActiveState.PENDING, "reserve"),

    (PurchaseActiveState.RESERVED, "pay"),
    
    (PurchaseActiveState.PAID, "claim"),
    (PurchaseActiveState.PAID, "unclaim"),
    (PurchaseActiveState.PAID, "refund"),
    
    (PurchaseActiveState.UNCLAIMED, "refund"),
])
def test_valid_transitions(from_state: PurchaseActiveState, method: str, 
                           customer_order_factory: Callable[[], PurchaseActive],
                           transition_order_to_state: Callable[[PurchaseActive, PurchaseActiveState], None], 
                           potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    transition_order_to_state(order, from_state)
    
    getattr(order, method)()


@pytest.mark.parametrize("from_state, method", [
    (PurchaseActiveState.PENDING, "pay"),
    (PurchaseActiveState.PENDING, "claim"),
    (PurchaseActiveState.PENDING, "unclaim"),
    (PurchaseActiveState.PENDING, "refund"),
    (PurchaseActiveState.PENDING, "cancel"),
    
    (PurchaseActiveState.RESERVED, "reserve"),
    (PurchaseActiveState.RESERVED, "claim"),
    (PurchaseActiveState.RESERVED, "unclaim"),
    (PurchaseActiveState.RESERVED, "refund"),
    
    (PurchaseActiveState.PAID, "reserve"),
    (PurchaseActiveState.PAID, "pay"),
    (PurchaseActiveState.PAID, "cancel"),
    
    (PurchaseActiveState.CLAIMED, "reserve"),
    (PurchaseActiveState.CLAIMED, "pay"),
    (PurchaseActiveState.CLAIMED, "claim"),
    (PurchaseActiveState.CLAIMED, "unclaim"),
    (PurchaseActiveState.CLAIMED, "refund"),
    (PurchaseActiveState.CLAIMED, "cancel"),
    
    (PurchaseActiveState.CANCELLED, "reserve"),
    (PurchaseActiveState.CANCELLED, "pay"),
    (PurchaseActiveState.CANCELLED, "claim"),
    (PurchaseActiveState.CANCELLED, "unclaim"),
    (PurchaseActiveState.CANCELLED, "refund"),
    (PurchaseActiveState.CANCELLED, "cancel"),
])
def test_invalid_transitions(from_state: PurchaseActiveState, method: str, 
                             customer_order_factory: Callable[[], PurchaseActive], 
                             transition_order_to_state: Callable[[PurchaseActive, PurchaseActiveState], None], 
                             potatoes_store_item_10: Callable[[], StoreItem],) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    transition_order_to_state(order, from_state)
        
    with pytest.raises(DomainException):
        getattr(order, method)()
    

@pytest.mark.parametrize("from_state, method", [
    (PurchaseActiveState.PENDING, "can_be_reserved"),

    (PurchaseActiveState.RESERVED, "can_be_paid"),
    
    (PurchaseActiveState.PAID, "can_be_claimed"),
    (PurchaseActiveState.PAID, "can_be_unclaimed"),
    (PurchaseActiveState.PAID, "can_be_refunded"),
    
    (PurchaseActiveState.UNCLAIMED, "can_be_refunded"),
])
def test_valid_checks(from_state: PurchaseActiveState, method: str, 
                      customer_order_factory: Callable[[], PurchaseActive], 
                      transition_order_to_state: Callable[[PurchaseActive, PurchaseActiveState], None], 
                      potatoes_store_item_10: Callable[[], StoreItem],) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    transition_order_to_state(order, from_state)
    
    assert getattr(order, method)()


@pytest.mark.parametrize("from_state, method", [
    (PurchaseActiveState.PENDING, "can_be_paid"),
    (PurchaseActiveState.PENDING, "can_be_claimed"),
    (PurchaseActiveState.PENDING, "can_be_cancelled"),
    
    (PurchaseActiveState.RESERVED, "can_be_reserved"),
    (PurchaseActiveState.RESERVED, "can_be_claimed"),
    
    (PurchaseActiveState.PAID, "can_be_reserved"),
    (PurchaseActiveState.PAID, "can_be_paid"),
    
    (PurchaseActiveState.CLAIMED, "can_be_reserved"),
    (PurchaseActiveState.CLAIMED, "can_be_paid"),
    (PurchaseActiveState.CLAIMED, "can_be_claimed"),
    (PurchaseActiveState.CLAIMED, "can_be_cancelled"),
    
    (PurchaseActiveState.CANCELLED, "can_be_reserved"),
    (PurchaseActiveState.CANCELLED, "can_be_paid"),
    (PurchaseActiveState.CANCELLED, "can_be_claimed"),
    (PurchaseActiveState.CANCELLED, "can_be_cancelled"),
])
def test_invalid_checks(from_state: PurchaseActiveState, method: str, 
                        customer_order_factory: Callable[[], PurchaseActive],
                        transition_order_to_state: Callable[[PurchaseActive, PurchaseActiveState], None], 
                        potatoes_store_item_10: Callable[[], StoreItem],) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = customer_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store_id=store_item.store_id)
    
    transition_order_to_state(order, from_state)
        
    assert not getattr(order, method)()