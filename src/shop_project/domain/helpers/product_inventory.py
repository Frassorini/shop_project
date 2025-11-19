from collections.abc import Sequence
from shop_project.shared.entity_id import EntityId
from shop_project.domain.exceptions import DomainException
from shop_project.domain.interfaces.stock_item import StockItem
from shop_project.domain.entities.product import Product


class ProductInventory:
    def __init__(self, stock: Sequence[Product]) -> None:
        self._stock: dict[EntityId, Product] = {item.entity_id: item for item in stock}

    def _ensure_stock_is_valid(self, items: Sequence[StockItem]) -> None:
        for order_item in items:
            if order_item.product_id not in self._stock.keys():
                raise DomainException("Invalid stock")
            
    def _ensure_stock_is_sufficient(self, items: Sequence[StockItem]) -> None:
        for order_item in items:
            if order_item.amount > self._stock[order_item.product_id].amount:
                raise DomainException("Insufficient stock")
    
    def _decrease_stock(self, items: Sequence[StockItem]) -> None:
        for order_item in items:
            self._stock[order_item.product_id].reserve(order_item.amount)
            
    def _increase_stock(self, items: Sequence[StockItem]) -> None:
        for order_item in items:
            self._stock[order_item.product_id].restock(order_item.amount)

    def reserve_stock(self, items: Sequence[StockItem]) -> None:
        self._ensure_stock_is_valid(items)
        self._ensure_stock_is_sufficient(items)
        self._decrease_stock(items)
    
    def restock(self, items: Sequence[StockItem]) -> None: 
        self._ensure_stock_is_valid(items)
        self._increase_stock(items)
    
    def check_stock_validity(self, items: Sequence[StockItem]) -> None:
        self._ensure_stock_is_valid(items)
    
    def get_item(self, product_id: EntityId) -> Product:
        return self._stock[product_id]