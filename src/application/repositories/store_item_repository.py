from typing import Any
from application.repositories.p_repository import PRepository
from domain.store_item.model import StoreItem
from shared.entity_id import EntityId


class StoreItemRepository(PRepository[StoreItem]):
    model_type = StoreItem
    
    def __init__(self, items: dict[EntityId, StoreItem]) -> None:
        self._items = items
    
    def get_by_criteria(self, criteria: str, values: list[Any]) -> list[StoreItem]:
        return [item for item in self._items.values() if getattr(item, criteria) in values]
    
    def fill(self, items: list[StoreItem]) -> None:
        for item in items:
            self._items[item.entity_id] = item