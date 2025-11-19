from typing import Any, Mapping, Type

from shop_project.domain.persistable_entity import PersistableEntity
from shop_project.domain.customer import Customer
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.purchase_summary import PurchaseSummary
from shop_project.domain.escrow_account import EscrowAccount
from shop_project.domain.product import Product
from shop_project.domain.shipment import Shipment
from shop_project.domain.shipment_summary import ShipmentSummary

from shop_project.infrastructure.repositories.base_repository import BaseRepository
from shop_project.infrastructure.repositories.mock_repository import MockRepository
from shop_project.infrastructure.repositories.customer_repository import CustomerRepository
from shop_project.infrastructure.repositories.purchase_draft_repository import PurchaseDraftRepository
from shop_project.infrastructure.repositories.purchase_active_repository import PurchaseActiveRepository
from shop_project.infrastructure.repositories.purchase_summary_repository import PurchaseSummaryRepository
from shop_project.infrastructure.repositories.escrow_account_repository import EscrowAccountRepository
from shop_project.infrastructure.repositories.product_repository import ProductRepository
from shop_project.infrastructure.repositories.shipment_repository import ShipmentRepository
from shop_project.infrastructure.repositories.shipment_summary_repository import ShipmentSummaryRepository


_REGISTRY: Mapping[Type[PersistableEntity], Type[BaseRepository[Any]]] = {
    Customer: CustomerRepository,
    PurchaseDraft: PurchaseDraftRepository,
    PurchaseActive: PurchaseActiveRepository,
    PurchaseSummary: PurchaseSummaryRepository,
    EscrowAccount: EscrowAccountRepository,
    Product: ProductRepository,
    Shipment: ShipmentRepository,
    ShipmentSummary: ShipmentSummaryRepository
}


class RepositoryRegistry:
    @classmethod
    def get_map(cls) -> Mapping[Type[PersistableEntity], Type[BaseRepository[Any]]]:
        return _REGISTRY