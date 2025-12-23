from typing import TypeVar, overload

from shop_project.application.dto.account_dto import AccountDTO
from shop_project.application.dto.auth_session_dto import AuthSessionDTO
from shop_project.application.dto.base_dto import BaseDTO, DTODynamicRegistry
from shop_project.application.dto.claim_token_dto import ClaimTokenDTO
from shop_project.application.dto.customer_dto import CustomerDTO
from shop_project.application.dto.employee_dto import EmployeeDTO
from shop_project.application.dto.escrow_account_dto import EscrowAccountDTO
from shop_project.application.dto.external_id_totp_dto import ExternalIdTotpDTO
from shop_project.application.dto.manager_dto import ManagerDTO
from shop_project.application.dto.product_dto import ProductDTO
from shop_project.application.dto.purchase_active_dto import (
    PurchaseActiveDTO,
)
from shop_project.application.dto.purchase_draft_dto import (
    PurchaseDraftDTO,
)
from shop_project.application.dto.purchase_summary_dto import (
    PurchaseSummaryDTO,
)
from shop_project.application.dto.shipment_dto import ShipmentDTO
from shop_project.application.dto.shipment_summary_dto import (
    ShipmentSummaryDTO,
)
from shop_project.application.dto.task_dto import TaskDTO
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.escrow_account import (
    EscrowAccount,
)
from shop_project.domain.entities.manager import Manager
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import (
    PurchaseActive,
)
from shop_project.domain.entities.purchase_draft import (
    PurchaseDraft,
)
from shop_project.domain.entities.purchase_summary import (
    PurchaseSummary,
)
from shop_project.domain.entities.shipment import Shipment
from shop_project.domain.entities.shipment_summary import (
    ShipmentSummary,
)
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.entities.account import Account
from shop_project.infrastructure.entities.auth_session import AuthSession
from shop_project.infrastructure.entities.claim_token import ClaimToken
from shop_project.infrastructure.entities.external_id_totp import ExternalIdTotp
from shop_project.infrastructure.entities.task import Task

T = TypeVar("T", bound=PersistableEntity)


@overload
def to_dto(entity: Task) -> TaskDTO: ...
@overload
def to_dto(entity: ClaimToken) -> ClaimTokenDTO: ...
@overload
def to_dto(entity: ExternalIdTotp) -> ExternalIdTotpDTO: ...
@overload
def to_dto(entity: Account) -> AccountDTO: ...
@overload
def to_dto(entity: Customer) -> CustomerDTO: ...
@overload
def to_dto(entity: Manager) -> ManagerDTO: ...
@overload
def to_dto(entity: Employee) -> EmployeeDTO: ...
@overload
def to_dto(entity: PurchaseDraft) -> PurchaseDraftDTO: ...
@overload
def to_dto(entity: PurchaseActive) -> PurchaseActiveDTO: ...
@overload
def to_dto(entity: PurchaseSummary) -> PurchaseSummaryDTO: ...
@overload
def to_dto(entity: EscrowAccount) -> EscrowAccountDTO: ...
@overload
def to_dto(entity: Product) -> ProductDTO: ...
@overload
def to_dto(entity: Shipment) -> ShipmentDTO: ...
@overload
def to_dto(entity: ShipmentSummary) -> ShipmentSummaryDTO: ...
@overload
def to_dto(entity: AuthSession) -> AuthSessionDTO: ...
@overload
def to_dto(entity: T) -> BaseDTO[T]: ...
def to_dto(entity: T) -> BaseDTO[T]:
    return DTODynamicRegistry.get(entity.__class__).model_validate(entity)


def to_domain(dto: BaseDTO[T]) -> T:
    return dto.to_domain()
