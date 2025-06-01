from datetime import datetime, timezone
import pytest

from domain.exceptions import DomainException, StateException
from domain.p_store_item import PStoreItem
from domain.supplier_order_item import SupplierOrderItem
from domain.supplier_order import SupplierOrder, SupplierOrderState


def test_supplier_order(potatoes_store_item_10: PStoreItem) -> None:
    potatoes = SupplierOrderItem(store_item=potatoes_store_item_10, amount=10)
    
    order = SupplierOrder(store='Moscow')
    order += potatoes
    assert order.state == SupplierOrderState.PENDING


def test_transitions_depart(supplier_order: SupplierOrder) -> None:
    supplier_order.depart(departure=datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc), 
                          arrival=datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc))
    assert supplier_order.state == SupplierOrderState.DEPARTED

    supplier_order.receive()
    with pytest.raises(StateException):
        supplier_order.depart(departure=datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc), 
                              arrival=datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc))


def test_transitions_receive(supplier_order: SupplierOrder) -> None:
    with pytest.raises(StateException):
        supplier_order.receive()
    
    supplier_order.depart(departure=datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc), 
                          arrival=datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc))
    
    supplier_order.receive()
    
    assert supplier_order.state == SupplierOrderState.RECEIVED


def test_cancel(supplier_order: SupplierOrder) -> None:
    supplier_order.cancel()
    assert supplier_order.state == SupplierOrderState.CANCELLED


def test_receive_add_amount_to_store_item(potatoes_store_item_10: PStoreItem) -> None:
    potatoes = SupplierOrderItem(store_item=potatoes_store_item_10, amount=10)
    supplier_order = SupplierOrder(store='Moscow')
    supplier_order += potatoes
    
    supplier_order.depart(departure=datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc), 
                          arrival=datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc))
    supplier_order.receive()
    
    assert potatoes_store_item_10.amount == 20


def test_add_to_order(potatoes_store_item_10: PStoreItem) -> None:
    potatoes = SupplierOrderItem(store_item=potatoes_store_item_10, amount=10)
    supplier_order = SupplierOrder(store='Moscow')
    supplier_order += potatoes
    
    potatoes_2 = SupplierOrderItem(store_item=potatoes_store_item_10, amount=10)
    supplier_order += potatoes_2
    
    assert len(supplier_order.items) == 2


def test_subtract_from_order(potatoes_store_item_10: PStoreItem) -> None:
    potatoes = SupplierOrderItem(store_item=potatoes_store_item_10, amount=10)
    supplier_order = SupplierOrder(store='Moscow')
    supplier_order += potatoes
    
    supplier_order -= potatoes
    
    assert len(supplier_order.items) == 0
    

def test_raise_invalid_store(potatoes_store_item_10_petersburg: PStoreItem) -> None:
    potatoes = SupplierOrderItem(store_item=potatoes_store_item_10_petersburg, amount=10)
    supplier_order = SupplierOrder(store='Moscow')
    
    with pytest.raises(DomainException):
        supplier_order += potatoes