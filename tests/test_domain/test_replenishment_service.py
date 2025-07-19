from typing import Callable

import pytest
from shop_project.domain.exceptions import DomainException
from shop_project.domain.services.replenishment_service import ReplenishmentService
from shop_project.domain.services.inventory_service import InventoryService
from shop_project.domain.store_item import StoreItem
from shop_project.domain.supplier_order import SupplierOrder

def test_(potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_10()
    inventory_service = InventoryService([potatoes])
    replenishment_service = ReplenishmentService(inventory_service)


def test_replenish(supplier_order_factory: Callable[[], SupplierOrder], 
                   potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_10()
    order = supplier_order_factory()
    order.add_item(store_item_id=potatoes.entity_id, amount=2, store_id=potatoes.store_id)
    inventory_service = InventoryService([potatoes])
    replenishment_service = ReplenishmentService(inventory_service)
    order.depart()

    replenishment_service.replenish(order)

    assert potatoes.amount == 12


def test_wrong_replenish(supplier_order_factory: Callable[[], SupplierOrder], 
                          potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_10()
    order = supplier_order_factory()
    order.add_item(store_item_id=potatoes.entity_id, amount=2, store_id=potatoes.store_id)
    inventory_service = InventoryService([potatoes])
    replenishment_service = ReplenishmentService(inventory_service)

    with pytest.raises(DomainException):
        replenishment_service.replenish(order)