from typing import Any, Callable, Literal, Type, TypeVar

import pytest
from application.interfaces.p_repository import PRepository
from domain.customer_order import CustomerOrder
from domain.customer import Customer
from domain.supplier_order import SupplierOrder
from domain.cart import Cart
import copy

from domain.store_item import StoreItem
from shared.entity_id import EntityId


ModelType = TypeVar('ModelType', 
    Customer,
    CustomerOrder,
    SupplierOrder,
    Cart,
    StoreItem,
    )


class FakeRepository(PRepository[ModelType]):    
    def __init__(self, model_type: Type[ModelType], items: list[ModelType]) -> None:
        self.model_type: Type[ModelType] = model_type
        self._items: dict[EntityId, dict[str, Any]] = {}
        self.fill(items)
    
    @classmethod
    def from_dict(cls, model_type: Type[ModelType], items: dict[EntityId, dict[str, Any]]) -> PRepository[ModelType]:
        obj = cls.__new__(cls)
        obj._items = items
        obj.model_type = model_type
        return obj
    
    def clone(self) -> PRepository[ModelType]:
        return self.__class__.from_dict(self.model_type, copy.deepcopy(self._items))
    
    def create(self, items: list[ModelType]) -> None:
        for item in items:
            self._items[item.entity_id] = item.snapshot()
    
    def read_by_attribute(self, attribute_name: str, values: list[Any]) -> list[ModelType]:
        result: list[ModelType] = []
        for item in self._items.values():
            if item[attribute_name] in values:
                result.append(self.model_type.from_snapshot(item))
            elif attribute_name == 'entity_id':
                if EntityId.from_str(item[attribute_name]) in values:
                    result.append(self.model_type.from_snapshot(item))
        return result
    
    def update(self, items: list[ModelType]) -> None:
        for item in items:
            self._items[item.entity_id] = item.snapshot()
    
    def delete(self, items: list[ModelType]) -> None:
        for item in items:
            self._items.pop(item.entity_id)
    
    def delete_by_attribute(self, attribute_name: str, values: list[Any]) -> None:
        to_delete = [
            EntityId.from_str(item['entity_id'])
            for item in self._items.values() 
            if getattr(item, attribute_name) in values
        ]
        for entity_id in to_delete:
            self._items.pop(entity_id)
    
    def fill(self, items: list[ModelType]) -> None:
        for item in items:
            self._items[item.entity_id] = item.snapshot()
    
    def save(self, difference: dict[Literal['CREATED', 'UPDATED', 'DELETED'], list[dict[str, Any]]]) -> None:
        for item in difference['CREATED']:
            self.create([self.model_type.from_snapshot(item)])

        for item in difference['UPDATED']:
            self.update([self.model_type.from_snapshot(item)])

        for item in difference['DELETED']:
            self.delete([self.model_type.from_snapshot(item)])

@pytest.fixture
def fake_repository() -> Callable[[Type[ModelType], list[ModelType]], PRepository[ModelType]]:
    def factory(model_type: Type[ModelType], items: list[ModelType]) -> PRepository[ModelType]:
        return FakeRepository(model_type, items)
    
    return factory