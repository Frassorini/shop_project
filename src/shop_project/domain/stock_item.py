from typing import Protocol

from shop_project.shared.entity_id import EntityId


class StockItem(Protocol):
    store_item_id: EntityId
    amount: int