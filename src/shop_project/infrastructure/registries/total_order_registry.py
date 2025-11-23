from typing import Any, Type

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.manager import Manager
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.domain.entities.shipment import Shipment
from shop_project.domain.entities.shipment_summary import ShipmentSummary
from shop_project.domain.interfaces.persistable_entity import PersistableEntity

_REGISTRY: dict[Type[PersistableEntity], int] = {
    Manager: 0,
    Employee: 1,
    Customer: 2,
    PurchaseDraft: 3,
    PurchaseActive: 4,
    PurchaseSummary: 5,
    EscrowAccount: 6,
    Shipment: 7,
    ShipmentSummary: 8,
    Product: 9,
}


class TotalOrderRegistry:
    """Регистр агрегатов с фиксированным топологическим порядком зависимостей."""

    @classmethod
    def get_priority(cls, aggregate_type: Type[PersistableEntity]) -> int:
        """Возвращает числовой приоритет агрегата (меньше = раньше в порядке)."""
        return cls._get_map()[aggregate_type]

    @classmethod
    def forward(cls) -> list[Type[PersistableEntity]]:
        """
        Возвращает список агрегатов в порядке от независимых к зависимым.
        Подходит для операций загрузки, инициализации и валидации.
        """
        mapping = cls._get_map()
        return [a for a, _ in sorted(mapping.items(), key=lambda kv: kv[1])]

    @classmethod
    def backward(cls) -> list[Type[PersistableEntity]]:
        """
        Возвращает список агрегатов в порядке от зависимых к независимым.
        Подходит для операций сохранения, удаления, отката и очистки.
        """
        mapping = cls._get_map()
        return [
            a for a, _ in sorted(mapping.items(), key=lambda kv: kv[1], reverse=True)
        ]

    @classmethod
    def _get_map(cls) -> dict[Type[Any], int]:
        """Определяет фиксированный топологический порядок зависимостей."""
        return _REGISTRY
