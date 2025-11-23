from typing import Any

from plum import dispatch, overload

from shop_project.application.dto.base_dto import BaseDTO
from shop_project.application.dto.customer_dto import CustomerDTO
from shop_project.application.dto.employee_dto import EmployeeDTO
from shop_project.application.dto.escrow_account_dto import EscrowAccountDTO
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
def to_dto(domain_object: PersistableEntity) -> BaseDTO:
    raise NotImplementedError


@dispatch
def to_dto(domain_object: Any) -> Any:
    pass


@overload
def to_domain(dto_object: CustomerDTO) -> Customer:
    return Customer._load(  # type: ignore[access-private]
        entity_id=dto_object.entity_id,
        name=dto_object.name,
    )


@overload
def to_domain(dto_object: ManagerDTO) -> Manager:
    return Manager._load(  # type: ignore[access-private]
        entity_id=dto_object.entity_id,
        name=dto_object.name,
    )


@overload
def to_domain(dto_object: EmployeeDTO) -> Employee:
    return Employee._load(  # type: ignore[access-private]
        entity_id=dto_object.entity_id,
        name=dto_object.name,
    )


@overload
def to_domain(dto_object: PurchaseDraftDTO) -> PurchaseDraft:
    return PurchaseDraft._load(  # type: ignore[access-private]
        entity_id=dto_object.entity_id,
        state=PurchaseDraftState(dto_object.state),
        customer_id=dto_object.customer_id,
        items=[PurchaseDraftItem(**item.model_dump()) for item in dto_object.items],
    )


@overload
def to_domain(dto_object: PurchaseActiveDTO) -> PurchaseActive:
    return PurchaseActive._load(  # type: ignore[access-private]
        entity_id=dto_object.entity_id,
        state=PurchaseActiveState(dto_object.state),
        customer_id=dto_object.customer_id,
        escrow_account_id=dto_object.escrow_account_id,
        items=[PurchaseActiveItem(**item.model_dump()) for item in dto_object.items],
    )


@overload
def to_domain(dto_object: PurchaseSummaryDTO) -> PurchaseSummary:
    return PurchaseSummary._load(  # type: ignore[access-private]
        entity_id=dto_object.entity_id,
        customer_id=dto_object.customer_id,
        escrow_account_id=dto_object.escrow_account_id,
        reason=PurchaseSummaryReason(dto_object.reason),
        items=[PurchaseSummaryItem(**item.model_dump()) for item in dto_object.items],
    )


@overload
def to_domain(dto_object: EscrowAccountDTO) -> EscrowAccount:
    return EscrowAccount._load(  # type: ignore[access-private]
        entity_id=dto_object.entity_id,
        state=EscrowAccountState(dto_object.state),
        total_amount=dto_object.total_amount,
    )


@overload
def to_domain(dto_object: ProductDTO) -> Product:
    return Product._load(  # type: ignore[access-private]
        entity_id=dto_object.entity_id,
        name=dto_object.name,
        amount=dto_object.amount,
        price=dto_object.price,
    )


@overload
def to_domain(dto_object: ShipmentDTO) -> Shipment:
    return Shipment._load(  # type: ignore[access-private]
        entity_id=dto_object.entity_id,
        state=ShipmentState(dto_object.state),
        items=[ShipmentItem(**item.model_dump()) for item in dto_object.items],
    )


@overload
def to_domain(dto_object: ShipmentSummaryDTO) -> ShipmentSummary:
    return ShipmentSummary._load(  # type: ignore[access-private]
        entity_id=dto_object.entity_id,
        reason=ShipmentSummaryReason(dto_object.reason),
        items=[ShipmentSummaryItem(**item.model_dump()) for item in dto_object.items],
    )


@overload
def to_domain(dto_object: BaseDTO) -> PersistableEntity:
    raise NotImplementedError


@dispatch
def to_domain(dto_object: BaseDTO) -> Any:
    pass
