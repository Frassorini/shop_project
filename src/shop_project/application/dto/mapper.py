from typing import Any, Type

from plum import overload, dispatch

from shop_project.application.dto.base_dto import BaseDTO
from shop_project.application.dto.customer_dto import CustomerDTO
from shop_project.application.dto.purchase_draft_dto import PurchaseDraftDTO
from shop_project.application.dto.purchase_active_dto import PurchaseActiveDTO
from shop_project.application.dto.escrow_account_dto import EscrowAccountDTO
from shop_project.application.dto.purchase_summary_dto import PurchaseSummaryDTO
from shop_project.application.dto.product_dto import ProductDTO
from shop_project.application.dto.shipment_dto import ShipmentDTO
from shop_project.application.dto.shipment_summary_dto import ShipmentSummaryDTO

from shop_project.domain.persistable_entity import PersistableEntity
from shop_project.domain.customer import Customer
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.purchase_summary import PurchaseSummary
from shop_project.domain.escrow_account import EscrowAccount
from shop_project.domain.product import Product
from shop_project.domain.shipment import Shipment
from shop_project.domain.shipment_summary import ShipmentSummary


@overload
def to_dto(domain_object: Customer) -> CustomerDTO:
    return CustomerDTO.model_validate(domain_object.to_dict())
@overload
def to_dto(domain_object: PurchaseDraft) -> PurchaseDraftDTO:
    return PurchaseDraftDTO.model_validate(domain_object.to_dict())
@overload
def to_dto(domain_object: PurchaseActive) -> PurchaseActiveDTO:
    return PurchaseActiveDTO.model_validate(domain_object.to_dict())
@overload
def to_dto(domain_object: PurchaseSummary) -> PurchaseSummaryDTO:
    return PurchaseSummaryDTO.model_validate(domain_object.to_dict())
@overload
def to_dto(domain_object: EscrowAccount) -> EscrowAccountDTO:
    return EscrowAccountDTO.model_validate(domain_object.to_dict())
@overload
def to_dto(domain_object: Product) -> ProductDTO:
    return ProductDTO.model_validate(domain_object.to_dict())
@overload
def to_dto(domain_object: Shipment) -> ShipmentDTO:
    return ShipmentDTO.model_validate(domain_object.to_dict())
@overload
def to_dto(domain_object: ShipmentSummary) -> ShipmentSummaryDTO:
    return ShipmentSummaryDTO.model_validate(domain_object.to_dict())
@overload
def to_dto(domain_object: PersistableEntity) -> BaseDTO:
    raise NotImplementedError

@dispatch
def to_dto(domain_object: Any) -> Any:
    pass


@overload
def to_domain(dto_object: CustomerDTO) -> Customer:
    return Customer.from_dict(dto_object.model_dump())
@overload
def to_domain(dto_object: PurchaseDraftDTO) -> PurchaseDraft:
    return PurchaseDraft.from_dict(dto_object.model_dump())
@overload
def to_domain(dto_object: PurchaseActiveDTO) -> PurchaseActive:
    return PurchaseActive.from_dict(dto_object.model_dump())
@overload
def to_domain(dto_object: PurchaseSummaryDTO) -> PurchaseSummary:
    return PurchaseSummary.from_dict(dto_object.model_dump())
@overload
def to_domain(dto_object: EscrowAccountDTO) -> EscrowAccount:
    return EscrowAccount.from_dict(dto_object.model_dump())
@overload
def to_domain(dto_object: ProductDTO) -> Product:
    return Product.from_dict(dto_object.model_dump())
@overload
def to_domain(dto_object: ShipmentDTO) -> Shipment:
    return Shipment.from_dict(dto_object.model_dump())
@overload
def to_domain(dto_object: ShipmentSummaryDTO) -> ShipmentSummary:
    return ShipmentSummary.from_dict(dto_object.model_dump())
@overload
def to_domain(dto_object: BaseDTO) -> PersistableEntity:
    raise NotImplementedError

@dispatch
def to_domain(dto_object: BaseDTO) -> Any:
    pass
