from typing import Any

from plum import dispatch, overload

from shop_project.application.dto.account_dto import AccountDTO
from shop_project.application.dto.auth_session_dto import AuthSessionDTO
from shop_project.application.dto.base_dto import BaseDTO
from shop_project.application.dto.customer_dto import CustomerDTO
from shop_project.application.dto.employee_dto import EmployeeDTO
from shop_project.application.dto.escrow_account_dto import EscrowAccountDTO
from shop_project.application.dto.external_id_totp_dto import ExternalIdTotpDTO
from shop_project.application.dto.manager_dto import ManagerDTO
from shop_project.application.dto.product_dto import ProductDTO
from shop_project.application.dto.purchase_active_dto import (
    PurchaseActiveDTO,
    PurchaseActiveItemDTO,
)
from shop_project.application.dto.purchase_draft_dto import (
    PurchaseDraftDTO,
    PurchaseDraftItemDTO,
)
from shop_project.application.dto.purchase_summary_dto import (
    PurchaseSummaryDTO,
    PurchaseSummaryItemDTO,
)
from shop_project.application.dto.shipment_dto import ShipmentDTO, ShipmentItemDTO
from shop_project.application.dto.shipment_summary_dto import (
    ShipmentSummaryDTO,
    ShipmentSummaryItemDTO,
)
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.escrow_account import (
    EscrowAccount,
    EscrowAccountState,
)
from shop_project.domain.entities.manager import Manager
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import (
    PurchaseActive,
    PurchaseActiveItem,
    PurchaseActiveState,
)
from shop_project.domain.entities.purchase_draft import (
    PurchaseDraft,
    PurchaseDraftItem,
    PurchaseDraftState,
)
from shop_project.domain.entities.purchase_summary import (
    PurchaseSummary,
    PurchaseSummaryItem,
    PurchaseSummaryReason,
)
from shop_project.domain.entities.shipment import Shipment, ShipmentItem, ShipmentState
from shop_project.domain.entities.shipment_summary import (
    ShipmentSummary,
    ShipmentSummaryItem,
    ShipmentSummaryReason,
)
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.entities.account import Account, SubjectType
from shop_project.infrastructure.entities.auth_session import AuthSession
from shop_project.infrastructure.entities.external_id_totp import ExternalIdTotp


@overload
def to_dto(domain_object: ExternalIdTotp) -> ExternalIdTotpDTO:
    return ExternalIdTotpDTO(
        entity_id=domain_object.entity_id,
        external_id_type=domain_object.external_id_type,
        external_id=domain_object.external_id,
        totp_verifier=domain_object.totp_verifier,
        issued_at=domain_object.issued_at,
        expiration=domain_object.expiration,
    )


@overload
def to_dto(domain_object: Account) -> AccountDTO:
    return AccountDTO(
        entity_id=domain_object.entity_id,
        subject_type=domain_object.subject_type.value,
        password_verifier=domain_object.password_verifier,
        login=domain_object.login,
        email=domain_object.email,
        phone_number=domain_object.phone_number,
    )


@overload
def to_dto(domain_object: Customer) -> CustomerDTO:
    return CustomerDTO(
        entity_id=domain_object.entity_id,
        name=domain_object.name,
    )


@overload
def to_dto(domain_object: Manager) -> ManagerDTO:
    return ManagerDTO(
        entity_id=domain_object.entity_id,
        name=domain_object.name,
    )


@overload
def to_dto(domain_object: Employee) -> EmployeeDTO:
    return EmployeeDTO(
        entity_id=domain_object.entity_id,
        name=domain_object.name,
    )


@overload
def to_dto(domain_object: PurchaseDraft) -> PurchaseDraftDTO:
    return PurchaseDraftDTO(
        entity_id=domain_object.entity_id,
        state=domain_object.state.value,
        customer_id=domain_object.customer_id,
        items=[
            PurchaseDraftItemDTO.model_validate(item) for item in domain_object.items
        ],
    )


@overload
def to_dto(domain_object: PurchaseActive) -> PurchaseActiveDTO:
    return PurchaseActiveDTO(
        entity_id=domain_object.entity_id,
        state=domain_object.state.value,
        customer_id=domain_object.customer_id,
        escrow_account_id=domain_object.escrow_account_id,
        items=[
            PurchaseActiveItemDTO.model_validate(item) for item in domain_object.items
        ],
    )


@overload
def to_dto(domain_object: PurchaseSummary) -> PurchaseSummaryDTO:
    return PurchaseSummaryDTO(
        entity_id=domain_object.entity_id,
        customer_id=domain_object.customer_id,
        escrow_account_id=domain_object.escrow_account_id,
        reason=domain_object.reason.value,
        items=[
            PurchaseSummaryItemDTO.model_validate(item) for item in domain_object.items
        ],
    )


@overload
def to_dto(domain_object: EscrowAccount) -> EscrowAccountDTO:
    return EscrowAccountDTO(
        entity_id=domain_object.entity_id,
        state=domain_object.state.value,
        total_amount=domain_object.total_amount,
    )


@overload
def to_dto(domain_object: Product) -> ProductDTO:
    return ProductDTO(
        entity_id=domain_object.entity_id,
        name=domain_object.name,
        amount=domain_object.amount,
        price=domain_object.price,
    )


@overload
def to_dto(domain_object: Shipment) -> ShipmentDTO:
    return ShipmentDTO(
        entity_id=domain_object.entity_id,
        state=domain_object.state.value,
        items=[ShipmentItemDTO.model_validate(item) for item in domain_object.items],
    )


@overload
def to_dto(domain_object: ShipmentSummary) -> ShipmentSummaryDTO:
    return ShipmentSummaryDTO(
        entity_id=domain_object.entity_id,
        reason=domain_object.reason.value,
        items=[
            ShipmentSummaryItemDTO.model_validate(item) for item in domain_object.items
        ],
    )


@overload
def to_dto(domain_object: AuthSession) -> AuthSessionDTO:
    return AuthSessionDTO(
        entity_id=domain_object.entity_id,
        account_id=domain_object.account_id,
        refresh_token_fingerprint=domain_object.refresh_token_fingerprint,
        issued_at=domain_object.issued_at,
        expiration=domain_object.expiration,
    )


@overload
def to_dto(domain_object: PersistableEntity) -> BaseDTO:
    raise NotImplementedError


@dispatch
def to_dto(domain_object: Any) -> Any:
    pass


@overload
def to_domain(dto_object: ExternalIdTotpDTO) -> ExternalIdTotp:
    return ExternalIdTotp.load(
        entity_id=dto_object.entity_id,
        external_id_type=dto_object.external_id_type,
        external_id=dto_object.external_id,
        totp_verifier=dto_object.totp_verifier,
        issued_at=dto_object.issued_at,
        expiration=dto_object.expiration,
    )


@overload
def to_domain(dto_object: AccountDTO) -> Account:
    return Account.load(
        entity_id=dto_object.entity_id,
        subject_type=SubjectType(dto_object.subject_type),
        password_verifier=dto_object.password_verifier,
        login=dto_object.login,
        email=dto_object.email,
        phone=dto_object.phone_number,
    )


@overload
def to_domain(dto_object: CustomerDTO) -> Customer:
    return Customer.load(
        entity_id=dto_object.entity_id,
        name=dto_object.name,
    )


@overload
def to_domain(dto_object: ManagerDTO) -> Manager:
    return Manager.load(
        entity_id=dto_object.entity_id,
        name=dto_object.name,
    )


@overload
def to_domain(dto_object: EmployeeDTO) -> Employee:
    return Employee.load(
        entity_id=dto_object.entity_id,
        name=dto_object.name,
    )


@overload
def to_domain(dto_object: PurchaseDraftDTO) -> PurchaseDraft:
    return PurchaseDraft.load(
        entity_id=dto_object.entity_id,
        state=PurchaseDraftState(dto_object.state),
        customer_id=dto_object.customer_id,
        items=[PurchaseDraftItem(**item.model_dump()) for item in dto_object.items],
    )


@overload
def to_domain(dto_object: PurchaseActiveDTO) -> PurchaseActive:
    return PurchaseActive.load(
        entity_id=dto_object.entity_id,
        state=PurchaseActiveState(dto_object.state),
        customer_id=dto_object.customer_id,
        escrow_account_id=dto_object.escrow_account_id,
        items=[PurchaseActiveItem(**item.model_dump()) for item in dto_object.items],
    )


@overload
def to_domain(dto_object: PurchaseSummaryDTO) -> PurchaseSummary:
    return PurchaseSummary.load(
        entity_id=dto_object.entity_id,
        customer_id=dto_object.customer_id,
        escrow_account_id=dto_object.escrow_account_id,
        reason=PurchaseSummaryReason(dto_object.reason),
        items=[PurchaseSummaryItem(**item.model_dump()) for item in dto_object.items],
    )


@overload
def to_domain(dto_object: EscrowAccountDTO) -> EscrowAccount:
    return EscrowAccount.load(
        entity_id=dto_object.entity_id,
        state=EscrowAccountState(dto_object.state),
        total_amount=dto_object.total_amount,
    )


@overload
def to_domain(dto_object: ProductDTO) -> Product:
    return Product.load(
        entity_id=dto_object.entity_id,
        name=dto_object.name,
        amount=dto_object.amount,
        price=dto_object.price,
    )


@overload
def to_domain(dto_object: ShipmentDTO) -> Shipment:
    return Shipment.load(
        entity_id=dto_object.entity_id,
        state=ShipmentState(dto_object.state),
        items=[ShipmentItem(**item.model_dump()) for item in dto_object.items],
    )


@overload
def to_domain(dto_object: ShipmentSummaryDTO) -> ShipmentSummary:
    return ShipmentSummary.load(
        entity_id=dto_object.entity_id,
        reason=ShipmentSummaryReason(dto_object.reason),
        items=[ShipmentSummaryItem(**item.model_dump()) for item in dto_object.items],
    )


@overload
def to_domain(dto_object: AuthSessionDTO) -> AuthSession:
    return AuthSession.load(
        entity_id=dto_object.entity_id,
        account_id=dto_object.account_id,
        refresh_token_fingerprint=dto_object.refresh_token_fingerprint,
        issued_at=dto_object.issued_at,
        expiration=dto_object.expiration,
    )


@overload
def to_domain(dto_object: BaseDTO) -> PersistableEntity:
    raise NotImplementedError


@dispatch
def to_domain(dto_object: BaseDTO) -> Any:
    pass
