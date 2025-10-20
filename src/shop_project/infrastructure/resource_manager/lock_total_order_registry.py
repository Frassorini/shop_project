from dataclasses import dataclass
from typing import Any, Callable, Generic, Type, TypeVar

from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.customer import Customer
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.store_item import StoreItem
from shop_project.domain.supplier_order import SupplierOrder


T = TypeVar('T')

class LockTotalOrderRegistry:
    @classmethod
    def get_priority(cls, aggregate_type: Type[BaseAggregate]) -> int:
        return cls._get_map()[aggregate_type]
    
    @classmethod
    def _get_map(cls) -> dict[Type[Any], int]:
        return {
            Customer: 0,
            PurchaseActive: 1,
            PurchaseDraft: 2,
            SupplierOrder: 3,
            StoreItem: 4,
        }