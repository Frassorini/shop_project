from datetime import datetime, timezone
from typing import Callable
import pytest

from domain.entity_id import EntityId
from domain.exceptions import DomainException, StateException
from domain.store_item import StoreItem
from domain.supplier_order_item import SupplierOrderItem
from domain.supplier_order import SupplierOrder, SupplierOrderState


from datetime import datetime, timezone

def test_supplier_order(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    potatoes = SupplierOrderItem(
        entity_id=unique_id_factory(),
        store_item=store_item,
        amount=10
    )
    
    order = SupplierOrder(entity_id=unique_id_factory(), store='Moscow')
    order += potatoes
    assert order.state == SupplierOrderState.PENDING


def test_transitions_depart(
    supplier_order_factory: Callable[[], SupplierOrder]
) -> None:
    order = supplier_order_factory()
    order.depart(
        departure=datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc),
        arrival=datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)
    )
    assert order.state == SupplierOrderState.DEPARTED

    order.receive()
    with pytest.raises(StateException):
        order.depart(
            departure=datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc),
            arrival=datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)
        )


def test_transitions_receive(
    supplier_order_factory: Callable[[], SupplierOrder]
) -> None:
    order = supplier_order_factory()
    with pytest.raises(StateException):
        order.receive()
    
    order.depart(
        departure=datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc),
        arrival=datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)
    )
    
    order.receive()
    assert order.state == SupplierOrderState.RECEIVED


def test_cancel(
    supplier_order_factory: Callable[[], SupplierOrder]
) -> None:
    order = supplier_order_factory()
    order.cancel()
    assert order.state == SupplierOrderState.CANCELLED


def test_receive_add_amount_to_store_item(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    potatoes = SupplierOrderItem(
        entity_id=unique_id_factory(),
        store_item=store_item,
        amount=10
    )
    supplier_order = SupplierOrder(entity_id=unique_id_factory(), store='Moscow')
    supplier_order += potatoes
    
    supplier_order.depart(
        departure=datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc),
        arrival=datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)
    )
    supplier_order.receive()
    
    assert store_item.amount == 20


def test_add_to_order(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    potatoes = SupplierOrderItem(
        entity_id=unique_id_factory(),
        store_item=store_item,
        amount=10
    )
    supplier_order = SupplierOrder(entity_id=unique_id_factory(), store='Moscow')
    supplier_order += potatoes
    
    potatoes_2 = SupplierOrderItem(
        entity_id=unique_id_factory(),
        store_item=store_item,
        amount=10
    )
    supplier_order += potatoes_2
    
    assert len(supplier_order.items) == 2


def test_subtract_from_order(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    store_item = potatoes_store_item_10()
    potatoes = SupplierOrderItem(
        entity_id=unique_id_factory(),
        store_item=store_item,
        amount=10
    )
    supplier_order = SupplierOrder(entity_id=unique_id_factory(), store='Moscow')
    supplier_order += potatoes
    
    supplier_order -= potatoes
    
    assert len(supplier_order.items) == 0
    

def test_raise_invalid_store(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[..., StoreItem]
) -> None:
    store_item = potatoes_store_item_10(store='Petersburg')
    potatoes = SupplierOrderItem(
        entity_id=unique_id_factory(),
        store_item=store_item,
        amount=10
    )
    supplier_order = SupplierOrder(entity_id=unique_id_factory(), store='Moscow')
    
    with pytest.raises(DomainException):
        supplier_order += potatoes