from typing import Callable

import pytest
from domain.exceptions import DomainException
from domain.services.replenishment_service import ReplenishmentService
from domain.store_item.inventory_service import InventoryService
from domain.store_item.model import StoreItem
from domain.supplier_order.model import SupplierOrder

def test_(potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_10()
    inventory_service = InventoryService([potatoes])
    replenishment_service = ReplenishmentService(inventory_service)


def test_replenish(supplier_order_factory: Callable[[], SupplierOrder], 
                   potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_10()
    order = supplier_order_factory()
    order.add_item(store_item_id=potatoes.entity_id, amount=2, store=potatoes.store)
    inventory_service = InventoryService([potatoes])
    replenishment_service = ReplenishmentService(inventory_service)
    order.depart()

    replenishment_service.replenish(order)

    assert potatoes.amount == 12


def test_wrong_replenish(supplier_order_factory: Callable[[], SupplierOrder], 
                          potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_10()
    order = supplier_order_factory()
    order.add_item(store_item_id=potatoes.entity_id, amount=2, store=potatoes.store)
    inventory_service = InventoryService([potatoes])
    replenishment_service = ReplenishmentService(inventory_service)

    with pytest.raises(DomainException):
        replenishment_service.replenish(order)