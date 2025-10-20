from typing import Callable

import pytest

from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.services.inventory_service import InventoryService
from shop_project.domain.exceptions import DomainException
from shop_project.domain.store_item import StoreItem
from shop_project.domain.supplier_order import SupplierOrder


def test_reserve_order(customer_order_factory: Callable[[], PurchaseActive],
                       potatoes_store_item_10: Callable[[], StoreItem], 
                       sausages_store_item_10: Callable[[], StoreItem],) -> None:
    potatoes: StoreItem = potatoes_store_item_10()
    sausages: StoreItem = sausages_store_item_10()
    inventory_service: InventoryService = InventoryService(stock=[potatoes, sausages])
    
    order = customer_order_factory()
    order.add_item(store_item_id=potatoes.entity_id, price=potatoes.price, amount=2)
    order.add_item(store_item_id=sausages.entity_id, price=sausages.price, amount=2)
    
    inventory_service.reserve_stock(order.get_items())
    
    assert potatoes.amount == 8
    assert sausages.amount == 8


def test_insufficient_stock(customer_order_factory: Callable[[], PurchaseActive],
                       potatoes_store_item_10: Callable[[], StoreItem], 
                       sausages_store_item_10: Callable[[], StoreItem],) -> None:
    potatoes: StoreItem = potatoes_store_item_10()
    sausages: StoreItem = sausages_store_item_10()
    inventory_service: InventoryService = InventoryService(stock=[potatoes, sausages])
    order = customer_order_factory()
    
    order.add_item(store_item_id=potatoes.entity_id, price=potatoes.price, amount=20)
    
    with pytest.raises(DomainException):
        inventory_service.reserve_stock(order.get_items())


def test_invalid_stock(customer_order_factory: Callable[[], PurchaseActive],
                       potatoes_store_item_10: Callable[[], StoreItem], 
                       sausages_store_item_10: Callable[[], StoreItem],) -> None:
    potatoes: StoreItem = potatoes_store_item_10()
    sausages: StoreItem = sausages_store_item_10()
    inventory_service: InventoryService = InventoryService(stock=[sausages])
    order = customer_order_factory()
    
    order.add_item(store_item_id=potatoes.entity_id, price=potatoes.price, amount=2)
    
    with pytest.raises(DomainException):
        inventory_service.reserve_stock(order.get_items())


def test_restock_customer(customer_order_factory: Callable[[], PurchaseActive],
                          potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes: StoreItem = potatoes_store_item_10()
    inventory_service: InventoryService = InventoryService(stock=[potatoes])
    order = customer_order_factory()
    order.add_item(store_item_id=potatoes.entity_id, price=potatoes.price, amount=2)
    
    inventory_service.reserve_stock(order.get_items())
    inventory_service.restock(order.get_items())
    
    assert potatoes.amount == 10


def test_restock_supplier(supplier_order_factory: Callable[[], SupplierOrder],
                          potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes: StoreItem = potatoes_store_item_10()
    inventory_service: InventoryService = InventoryService(stock=[potatoes])
    order = supplier_order_factory()
    order.add_item(store_item_id=potatoes.entity_id, amount=2)
    
    inventory_service.restock(order.get_items())
    
    assert potatoes.amount == 12


