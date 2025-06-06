from typing import Callable
import pytest

from domain.exceptions import DomainException
from domain.store_item.model import StoreItem
from domain.supplier_order import SupplierOrder, SupplierOrderState, SupplierOrderItem


def test_(supplier_order_factory: Callable[[], SupplierOrder]) -> None:
    order = supplier_order_factory()
    

def test_add_item(supplier_order_factory: Callable[[], SupplierOrder],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = supplier_order_factory()
    
    
    order.add_item(store_item_id=store_item.entity_id, amount=2, store=store_item.store)


def test_add_negative_amount(supplier_order_factory: Callable[[], SupplierOrder],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = supplier_order_factory()
    
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, amount=-2, store=store_item.store)


def test_get_item(supplier_order_factory: Callable[[], SupplierOrder],
                  potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = supplier_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, amount=2, store=store_item.store)
    
    order_item: SupplierOrderItem = order.get_item(store_item.entity_id)
    
    assert order_item.amount == 2


def test_cannot_add_duplicate_item(supplier_order_factory: Callable[[], SupplierOrder],
                                   potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = supplier_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, amount=2, store=store_item.store)
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, amount=3, store=store_item.store)


def test_cannot_add_from_another_store(supplier_order_factory: Callable[[], SupplierOrder],
                                       potatoes_store_item_10: Callable[..., StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10(store="Petersburg")
    order = supplier_order_factory()
    
    with pytest.raises(DomainException):
        order.add_item(store_item_id=store_item.entity_id, amount=2, store=store_item.store)
    

def test_valid_transitions(supplier_order_factory: Callable[[], SupplierOrder],
                           potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = supplier_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, amount=2, store=store_item.store)
    
    order.depart()
    
    order.receive()


@pytest.mark.parametrize("from_state, method", [
    (SupplierOrderState.PENDING, "receive"),
    (SupplierOrderState.PENDING, "cancel"),
    
    (SupplierOrderState.DEPARTED, "depart"),
    
    (SupplierOrderState.RECEIVED, "depart"),
    (SupplierOrderState.RECEIVED, "receive"),
    (SupplierOrderState.RECEIVED, "cancel"),
    
    (SupplierOrderState.CANCELLED, "depart"),
    (SupplierOrderState.CANCELLED, "receive"),
    (SupplierOrderState.CANCELLED, "cancel"),
])
def test_invalid_transitions(from_state: SupplierOrderState, method: str, 
                             supplier_order_factory: Callable[[], SupplierOrder],
                             potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = supplier_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, amount=2, store=store_item.store)
    
    match from_state:
        case SupplierOrderState.PENDING:
            pass
        case SupplierOrderState.DEPARTED:
            order.depart()
        case SupplierOrderState.RECEIVED:
            order.depart()
            order.receive()
        case SupplierOrderState.CANCELLED:
            order.depart()
            order.cancel()
        
    with pytest.raises(DomainException):
        getattr(order, method)()
    

def test_valid_checks(supplier_order_factory: Callable[[], SupplierOrder],
                      potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = supplier_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, amount=2, store=store_item.store)
    
    assert order.can_be_departed()
    assert not order.can_be_cancelled()
    order.depart()
    
    assert order.can_be_received()
    assert order.can_be_cancelled()
    order.receive()


@pytest.mark.parametrize("from_state, method", [
    (SupplierOrderState.PENDING, "can_be_received"),
    (SupplierOrderState.PENDING, "can_be_cancelled"),
    
    (SupplierOrderState.DEPARTED, "can_be_departed"),
    
    (SupplierOrderState.RECEIVED, "can_be_departed"),
    (SupplierOrderState.RECEIVED, "can_be_received"),
    (SupplierOrderState.RECEIVED, "can_be_cancelled"),
    
    (SupplierOrderState.CANCELLED, "can_be_departed"),
    (SupplierOrderState.CANCELLED, "can_be_received"),
    (SupplierOrderState.CANCELLED, "can_be_cancelled"),
])
def test_invalid_checks(from_state: SupplierOrderState, method: str, 
                        supplier_order_factory: Callable[[], SupplierOrder],
                        potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    store_item: StoreItem = potatoes_store_item_10()
    order = supplier_order_factory()
    
    order.add_item(store_item_id=store_item.entity_id, amount=2, store=store_item.store)
    
    match from_state:
        case SupplierOrderState.PENDING:
            pass
        case SupplierOrderState.DEPARTED:
            order.depart()
        case SupplierOrderState.RECEIVED:
            order.depart()
            order.receive()
        case SupplierOrderState.CANCELLED:
            order.depart()
            order.cancel()
        
    assert not getattr(order, method)()