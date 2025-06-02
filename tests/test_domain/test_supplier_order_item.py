from typing import Callable
import pytest
from domain.entity_id import EntityId
from domain.exceptions import StateException
from domain.store_item import StoreItem
from domain.supplier_order_item import SupplierOrderItem


def test_supplier_item(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    
    supply_item = SupplierOrderItem(
        entity_id=unique_id_factory(),
        store_item=store_item, 
        amount=10
    )
    
    assert supply_item.store_item == store_item
    assert supply_item.store == 'Moscow'


def test_receive_add_amount_to_store_item(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    supply_item = SupplierOrderItem(
        entity_id=unique_id_factory(),
        store_item=store_item, 
        amount=10
    )
    
    supply_item.receive()
    
    assert store_item.amount == 20


def test_double_receive(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    supply_item = SupplierOrderItem(
        entity_id=unique_id_factory(),
        store_item=store_item, 
        amount=10
    )
    
    supply_item.receive()
    with pytest.raises(StateException):
        supply_item.receive()
    