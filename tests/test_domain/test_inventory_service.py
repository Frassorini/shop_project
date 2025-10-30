from typing import Callable

import pytest

from shop_project.domain.services.inventory_service import InventoryService
from shop_project.domain.exceptions import DomainException
from shop_project.domain.product import Product
from shop_project.domain.stock_item import StockItem
from shop_project.shared.entity_id import EntityId


class AbstractStockItem(StockItem):
    def __init__(self, product_id: EntityId, amount: int) -> None:
        self.product_id = product_id
        self.amount = amount


def test_reserve_order(potatoes_product_10: Callable[[], Product], 
                       sausages_product_10: Callable[[], Product],) -> None:
    potatoes: Product = potatoes_product_10()
    sausages: Product = sausages_product_10()
    inventory_service: InventoryService = InventoryService(stock=[potatoes, sausages])
    
    items: list[StockItem] = [
        AbstractStockItem(potatoes.entity_id, 2), 
        AbstractStockItem(sausages.entity_id, 2)
    ]
    
    inventory_service.reserve_stock(items)
    
    assert potatoes.amount == 8
    assert sausages.amount == 8


def test_reserve_insufficient_stock(potatoes_product_10: Callable[[], Product], 
                            sausages_product_10: Callable[[], Product],) -> None:
    potatoes: Product = potatoes_product_10()
    sausages: Product = sausages_product_10()
    inventory_service: InventoryService = InventoryService(stock=[potatoes, sausages])
    
    items: list[StockItem] = [
        AbstractStockItem(potatoes.entity_id, 20), 
    ]
    
    with pytest.raises(DomainException):
        inventory_service.reserve_stock(items)


def test_reserve_invalid_stock(potatoes_product_10: Callable[[], Product], 
                       sausages_product_10: Callable[[], Product],) -> None:
    potatoes: Product = potatoes_product_10()
    sausages: Product = sausages_product_10()
    inventory_service: InventoryService = InventoryService(stock=[sausages])
    
    items: list[StockItem] = [
        AbstractStockItem(potatoes.entity_id, 2), 
    ]
    
    with pytest.raises(DomainException):
        inventory_service.reserve_stock(items)


def test_restock_invalid_stock(potatoes_product_10: Callable[[], Product], 
                 sausages_product_10: Callable[[], Product],) -> None:
    potatoes: Product = potatoes_product_10()
    sausages: Product = sausages_product_10()
    inventory_service: InventoryService = InventoryService(stock=[potatoes])
    
    items: list[StockItem] = [
        AbstractStockItem(potatoes.entity_id, 2), 
    ]
    
    inventory_service.reserve_stock(items)
    inventory_service.restock(items)
    
    assert potatoes.amount == 10


def test_restock_invalid_stock(potatoes_product_10: Callable[[], Product], 
                 sausages_product_10: Callable[[], Product],) -> None:
    potatoes: Product = potatoes_product_10()
    sausages: Product = sausages_product_10()
    inventory_service: InventoryService = InventoryService(stock=[potatoes])
    
    items: list[StockItem] = [
        AbstractStockItem(potatoes.entity_id, 2), 
    ]
    
    inventory_service.reserve_stock(items)
    with pytest.raises(DomainException):
        inventory_service.restock([AbstractStockItem(sausages.entity_id, 2)])
    
    assert sausages.amount == 10
