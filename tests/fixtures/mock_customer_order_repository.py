from typing import Any, Callable

import pytest
from domain.customer_order.model import CustomerOrder
from shared.entity_id import EntityId
from application.interfaces.p_repository import PRepository


class MockCustomerOrderRepository(PRepository[CustomerOrder]):
    model_type = CustomerOrder
    
    def __init__(self, items: list[CustomerOrder]) -> None:
        self._items: dict[EntityId, CustomerOrder] = {}
        self.fill(items)
    
    def create(self, items: list[CustomerOrder]) -> None:
        for order in items:
            self._items[order.entity_id] = order
    
    def read_by_attribute(self, attribute_name: str, values: list[Any]) -> list[CustomerOrder]:
        result: list[CustomerOrder] = []
        for order in self._items.values():
            if getattr(order, attribute_name) in values:
                result.append(order)
        return result
    
    def update(self, items: list[CustomerOrder]) -> None:
        for order in items:
            self._items[order.entity_id] = order
    
    def delete(self, items: list[CustomerOrder]) -> None:
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
    
    def fill(self, items: list[CustomerOrder]) -> None:
        for order in items:
            self._items[order.entity_id] = order


@pytest.fixture
def mock_customer_order_repository() -> Callable[[list[CustomerOrder]], PRepository[CustomerOrder]]:
    def factory(items: list[CustomerOrder]) -> PRepository[CustomerOrder]:
        return MockCustomerOrderRepository(items)
    
    return factory