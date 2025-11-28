from typing import Any, Mapping, Type

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
from shop_project.infrastructure.repositories.account_repository import (
    AccountRepository,
)
from shop_project.infrastructure.repositories.auth_session_repository import (
    AuthSessionRepository,
)
from shop_project.infrastructure.repositories.base_repository import BaseRepository
from shop_project.infrastructure.repositories.customer_repository import (
    CustomerRepository,
)
from shop_project.infrastructure.repositories.employee_repository import (
    EmployeeRepository,
)
from shop_project.infrastructure.repositories.escrow_account_repository import (
    EscrowAccountRepository,
)
from shop_project.infrastructure.repositories.manager_repository import (
    ManagerRepository,
)
from shop_project.infrastructure.repositories.product_repository import (
    ProductRepository,
)
from shop_project.infrastructure.repositories.purchase_active_repository import (
    PurchaseActiveRepository,
)
from shop_project.infrastructure.repositories.purchase_draft_repository import (
    PurchaseDraftRepository,
)
from shop_project.infrastructure.repositories.purchase_summary_repository import (
    PurchaseSummaryRepository,
)
from shop_project.infrastructure.repositories.secret_repository import SecretRepository
from shop_project.infrastructure.repositories.shipment_repository import (
    ShipmentRepository,
)
from shop_project.infrastructure.repositories.shipment_summary_repository import (
    ShipmentSummaryRepository,
)

_REGISTRY: Mapping[Type[PersistableEntity], Type[BaseRepository[Any, Any]]] = {
    Account: AccountRepository,
    AuthSession: AuthSessionRepository,
    Secret: SecretRepository,
    Manager: ManagerRepository,
    Employee: EmployeeRepository,
    Customer: CustomerRepository,
    PurchaseDraft: PurchaseDraftRepository,
    PurchaseActive: PurchaseActiveRepository,
    PurchaseSummary: PurchaseSummaryRepository,
    EscrowAccount: EscrowAccountRepository,
    Product: ProductRepository,
    Shipment: ShipmentRepository,
    ShipmentSummary: ShipmentSummaryRepository,
}


class RepositoryRegistry:
    @classmethod
    def get_map(
        cls,
    ) -> Mapping[Type[PersistableEntity], Type[BaseRepository[Any, Any]]]:
        return _REGISTRY
