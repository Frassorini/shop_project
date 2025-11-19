from typing import Protocol

from shop_project.shared.entity_id import EntityId


class StockItem(Protocol):
    product_id: EntityId
    amount: int
