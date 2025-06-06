from dataclasses import dataclass

from domain.stock_item import StockItem
from shared.entity_id import EntityId


@dataclass(frozen=True)
class SupplierOrderItem(StockItem):
    store_item_id: EntityId
    amount: int