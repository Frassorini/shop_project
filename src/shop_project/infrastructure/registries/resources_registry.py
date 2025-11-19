from typing import Type

from shop_project.domain.persistable_entity import PersistableEntity
from shop_project.domain.customer import Customer
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.purchase_summary import PurchaseSummary
from shop_project.domain.escrow_account import EscrowAccount
from shop_project.domain.product import Product
from shop_project.domain.shipment import Shipment
from shop_project.domain.shipment_summary import ShipmentSummary


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