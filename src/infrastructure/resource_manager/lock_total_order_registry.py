from dataclasses import dataclass
from typing import Any, Callable, Generic, Type, TypeVar

from domain.cart import Cart
from domain.customer import Customer
from domain.customer_order import CustomerOrder
from domain.p_aggregate import PAggregate
from domain.store_item import StoreItem
from domain.supplier_order import SupplierOrder
from domain.store import Store


T = TypeVar('T')

class LockTotalOrderRegistry:
    @classmethod
    def get_priority(cls, aggregate_type: Type[PAggregate]) -> int:
        return cls._get_map()[aggregate_type]
    
    @classmethod
    def _get_map(cls) -> dict[Type[Any], int]:
        return {
            Customer: 0,
            CustomerOrder: 1,
            Cart: 2,
            SupplierOrder: 3,
            Store: 4,
            StoreItem: 5,
        }