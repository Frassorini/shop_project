from typing import Type

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
from shop_project.infrastructure.entities.account import Account
from shop_project.infrastructure.entities.auth_session import AuthSession
from shop_project.infrastructure.entities.external_id_totp import ExternalIdTotp
from shop_project.infrastructure.entities.task import Task

_REGISTRY: list[Type[PersistableEntity]] = [
    Task,
    Account,
    ExternalIdTotp,
    AuthSession,
    Manager,
    Employee,
    Customer,
    PurchaseDraft,
    PurchaseActive,
    PurchaseSummary,
    EscrowAccount,
    Shipment,
    ShipmentSummary,
    Product,
]


class TotalOrderRegistry:
    """Регистр агрегатов с фиксированным топологическим порядком зависимостей."""

    @classmethod
    def get_priority(cls, aggregate_type: Type[PersistableEntity]) -> int:
        """Возвращает числовой приоритет агрегата (меньше = раньше в порядке)."""
        return cls._get_map().index(aggregate_type)

    @classmethod
    def forward(cls) -> list[Type[PersistableEntity]]:
        """
        Возвращает список агрегатов в порядке от независимых к зависимым.
        Подходит для операций загрузки, инициализации и валидации.
        """
        return cls._get_map()

    @classmethod
    def backward(cls) -> list[Type[PersistableEntity]]:
        """
        Возвращает список агрегатов в порядке от зависимых к независимым.
        Подходит для операций сохранения, удаления, отката и очистки.
        """
        return cls.forward()[::-1]

    @classmethod
    def _get_map(cls) -> list[Type[PersistableEntity]]:
        """Определяет фиксированный топологический порядок зависимостей."""
        return _REGISTRY
