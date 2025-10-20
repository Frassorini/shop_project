from typing import Any, Type

from plum import overload, dispatch

from shop_project.application.dto.customer_dto import CustomerDTO
from shop_project.application.dto.store_item_dto import StoreItemDTO
from shop_project.application.dto.purchase_draft_dto import PurchaseDraftDTO
from shop_project.application.dto.purchase_active_dto import PurchaseActiveDTO
from shop_project.application.dto.supplier_order_dto import SupplierOrderDTO
from shop_project.application.dto.base_dto import BaseDTO

from shop_project.domain.customer import Customer
from shop_project.domain.store_item import StoreItem
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.supplier_order import SupplierOrder
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.base_aggregate import BaseAggregate


@overload
def to_dto(domain_object: Customer) -> CustomerDTO:
    return CustomerDTO.model_validate(domain_object.to_dict())
@overload
def to_dto(domain_object: StoreItem) -> StoreItemDTO:
    return StoreItemDTO.model_validate(domain_object.to_dict())
@overload
def to_dto(domain_object: PurchaseDraft) -> PurchaseDraftDTO:
    return PurchaseDraftDTO.model_validate(domain_object.to_dict())
@overload
def to_dto(domain_object: PurchaseActive) -> PurchaseActiveDTO:
    return PurchaseActiveDTO.model_validate(domain_object.to_dict())
@overload
def to_dto(domain_object: SupplierOrder) -> SupplierOrderDTO:
    return SupplierOrderDTO.model_validate(domain_object.to_dict())
@overload
def to_dto(domain_object: BaseAggregate) -> BaseDTO:
    raise NotImplementedError

@dispatch
def to_dto(domain_object: Any) -> Any:
    pass


@overload
def to_domain(dto_object: CustomerDTO) -> Customer:
    return Customer.from_dict(dto_object.model_dump())
@overload
def to_domain(dto_object: StoreItemDTO) -> StoreItem:
    return StoreItem.from_dict(dto_object.model_dump())
@overload
def to_domain(dto_object: PurchaseDraftDTO) -> PurchaseDraft:
    return PurchaseDraft.from_dict(dto_object.model_dump())
@overload
def to_domain(dto_object: PurchaseActiveDTO) -> PurchaseActive:
    return PurchaseActive.from_dict(dto_object.model_dump())
@overload
def to_domain(dto_object: SupplierOrderDTO) -> SupplierOrder:
    return SupplierOrder.from_dict(dto_object.model_dump())
@overload
def to_domain(dto_object: BaseDTO) -> BaseAggregate:
    raise NotImplementedError

@dispatch
def to_domain(dto_object: BaseDTO) -> Any:
    pass
