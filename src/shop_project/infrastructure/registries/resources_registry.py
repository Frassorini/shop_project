from typing import Type

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.domain.entities.shipment import Shipment
from shop_project.domain.entities.shipment_summary import ShipmentSummary
from shop_project.domain.interfaces.persistable_entity import PersistableEntity

_REGISTRY: list[Type[PersistableEntity]] = [
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
        return [
            Customer,
            PurchaseActive,
            PurchaseDraft,
            PurchaseSummary,
            EscrowAccount,
            Product,
            Shipment,
            ShipmentSummary,
        ]
