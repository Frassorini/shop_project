from typing import Any, Callable

import pytest
from application.interfaces.p_repository import PRepository
from domain.store_item.model import StoreItem
from shared.entity_id import EntityId


class MockStoreItemRepository(PRepository[StoreItem]):
    model_type = StoreItem
    
    def __init__(self, items: list[StoreItem]) -> None:
        self._items: dict[EntityId, StoreItem] = {}
        self.fill(items)
    
    def create(self, items: list[StoreItem]) -> None:
        for item in items:
            self._items[item.entity_id] = item
    
    def read_by_attribute(self, attribute_name: str, values: list[Any]) -> list[StoreItem]:
        result: list[StoreItem] = []
        for item in self._items.values():
            if getattr(item, attribute_name) in values:
                result.append(item)
        return result
    
    def update(self, items: list[StoreItem]) -> None:
        for item in items:
            self._items[item.entity_id] = item
    
    def delete(self, items: list[StoreItem]) -> None:
        for item in items:
            self._items.pop(item.entity_id)
    
    def delete_by_attribute(self, attribute_name: str, values: list[Any]) -> None:
        to_delete = [
            item.entity_id 
            for item in self._items.values() 
            if getattr(item, attribute_name) in values
        ]
        for entity_id in to_delete:
            self._items.pop(entity_id)
    
    def fill(self, items: list[StoreItem]) -> None:
        for item in items:
            self._items[item.entity_id] = item


@pytest.fixture
def mock_store_item_repository() -> Callable[[list[StoreItem]], MockStoreItemRepository]:
    def factory(items: list[StoreItem]) -> MockStoreItemRepository:
        return MockStoreItemRepository(items)
    
    return factory