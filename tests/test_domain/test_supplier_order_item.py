import pytest
from domain.exceptions import StateException
from domain.p_store_item import PStoreItem
from domain.supplier_order_item import SupplierOrderItem


def test_supplier_item(potatoes_store_item_10: PStoreItem) -> None:
    potatoes_store_item_10.id_ = 1
    
    supply_item = SupplierOrderItem(potatoes_store_item_10, 10)
    
    assert supply_item.store_item == potatoes_store_item_10
    assert supply_item.store == 'Moscow'


def test_receive_add_amount_to_store_item(potatoes_store_item_10: PStoreItem) -> None:
    supply_item = SupplierOrderItem(potatoes_store_item_10, 10)
    
    supply_item.receive()
    
    assert potatoes_store_item_10.amount == 20


def test_double_receive(potatoes_store_item_10: PStoreItem) -> None:
    supply_item = SupplierOrderItem(potatoes_store_item_10, 10)
    
    supply_item.receive()
    with pytest.raises(StateException):
        supply_item.receive()
    