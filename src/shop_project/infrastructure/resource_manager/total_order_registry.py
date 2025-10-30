from dataclasses import dataclass
from typing import Any, Callable, Generic, Type, TypeVar

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.customer import Customer
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.purchase_summary import PurchaseSummary
from shop_project.domain.escrow_account import EscrowAccount
from shop_project.domain.store_item import StoreItem
from shop_project.domain.shipment import Shipment
from shop_project.domain.shipment_summary import ShipmentSummary


class TotalOrderRegistry:
    """Регистр агрегатов с фиксированным топологическим порядком зависимостей."""

    @classmethod
    def get_priority(cls, aggregate_type: Type[BaseAggregate]) -> int:
        """Возвращает числовой приоритет агрегата (меньше = раньше в порядке)."""
        return cls._get_map()[aggregate_type]

    @classmethod
    def forward(cls) -> list[Type[BaseAggregate]]:
        """
        Возвращает список агрегатов в порядке от независимых к зависимым.
        Подходит для операций загрузки, инициализации и валидации.
        """
        mapping = cls._get_map()
        return [a for a, _ in sorted(mapping.items(), key=lambda kv: kv[1])]

    @classmethod
    def backward(cls) -> list[Type[BaseAggregate]]:
        """
        Возвращает список агрегатов в порядке от зависимых к независимым.
        Подходит для операций сохранения, удаления, отката и очистки.
        """
        mapping = cls._get_map()
        return [a for a, _ in sorted(mapping.items(), key=lambda kv: kv[1], reverse=True)]

    @classmethod
    def _get_map(cls) -> dict[Type[Any], int]:
        """Определяет фиксированный топологический порядок зависимостей."""
        return {
            Customer: 0,
            PurchaseDraft: 1,
            PurchaseActive: 2,
            PurchaseSummary: 3,
            EscrowAccount: 4,
            Shipment: 5,
            ShipmentSummary: 6,
            StoreItem: 7,
        }