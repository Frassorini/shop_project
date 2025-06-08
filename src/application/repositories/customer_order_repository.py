from typing import Any
from domain.customer_order.model import CustomerOrder
from shared.entity_id import EntityId
from application.repositories.p_repository import PRepository


class CustomerOrderRepository(PRepository[CustomerOrder]):
    model_type = CustomerOrder
    
    def __init__(self, orders: dict[EntityId, CustomerOrder]) -> None:
        self._orders = orders
    
    def get_by_criteria(self, criteria: str, values: list[Any]) -> list[CustomerOrder]:
        return [order for order in self._orders.values() if getattr(order, criteria) in values]
    
    def fill(self, items: list[CustomerOrder]) -> None:
        for order in items:
            self._orders[order.entity_id] = order