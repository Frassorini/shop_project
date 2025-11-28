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
from shop_project.infrastructure.entities.secret import Secret

_REGISTRY: list[Type[PersistableEntity]] = [
    Account,
    AuthSession,
    Secret,
    Manager,
    Employee,
    Customer,
    PurchaseActive,
    PurchaseDraft,
    PurchaseSummary,
    EscrowAccount,
    Product,
    Shipment,
    ShipmentSummary,
]


class ResourcesRegistry:
    @classmethod
    def get_map(cls) -> list[Type[PersistableEntity]]:
        return _REGISTRY
