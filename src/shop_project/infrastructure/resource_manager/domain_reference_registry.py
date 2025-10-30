from dataclasses import dataclass
from typing import Any, Callable, Generic, Type, TypeVar

from shop_project.domain.customer import Customer
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.purchase_summary import PurchaseSummary
from shop_project.domain.escrow_account import EscrowAccount
from shop_project.domain.product import Product
from shop_project.domain.shipment import Shipment
from shop_project.domain.shipment_summary import ShipmentSummary


SourceType = TypeVar('SourceType')
TargetType = TypeVar('TargetType')

@dataclass(frozen=True)
class DomainReferenceDescriptor(Generic[SourceType]):
    attribute_name: str
    strategy: Callable[[SourceType], list[Any]]


class DomainReferenceRegistry():

    @classmethod
    def get_reference_descriptor(cls, source_type: Type[SourceType], target_type: Type[TargetType]) -> DomainReferenceDescriptor[SourceType]:
        if source_type not in cls._get_map():
            raise NotImplementedError(f"No descriptor for {source_type}")
        if target_type not in cls._get_map()[source_type]:
            raise NotImplementedError(f"No descriptor for {source_type} -> {target_type}")
        
        return cls._get_map()[source_type][target_type]

    @classmethod
    def _get_map(cls) -> dict[Type[Any], dict[Type[Any], DomainReferenceDescriptor[Any]]]:
        return {
            Customer: {
                PurchaseActive: DomainReferenceDescriptor(
                    attribute_name="customer_id",
                    strategy=lambda customer: [customer.entity_id.value]
                ),
                PurchaseDraft: DomainReferenceDescriptor(
                    attribute_name="customer_id",
                    strategy=lambda customer: [customer.entity_id.value]
                ),
                PurchaseSummary: DomainReferenceDescriptor(
                    attribute_name="customer_id",
                    strategy=lambda customer: [customer.entity_id.value]
                ),
                EscrowAccount: DomainReferenceDescriptor(
                    attribute_name="customer_id",
                    strategy=lambda customer: [customer.entity_id.value]
                ),
            },
            PurchaseDraft: {
                Product: DomainReferenceDescriptor(
                    attribute_name="entity_id",
                    strategy=lambda cart: [item.product_id.value for item in cart.get_items()]
                ),
            },
            PurchaseActive: {
                Product: DomainReferenceDescriptor(
                    attribute_name="entity_id",
                    strategy=lambda order: [item.product_id.value for item in order.get_items()],
                ),
                EscrowAccount: DomainReferenceDescriptor(
                    attribute_name="entity_id",
                    strategy=lambda order: [order.escrow_account_id.value],
                ),
            },
            PurchaseSummary: {
                Product: DomainReferenceDescriptor(
                    attribute_name="entity_id",
                    strategy=lambda order: [item.product_id.value for item in order.get_items()]
                ),
            },
            EscrowAccount: {
                PurchaseSummary: DomainReferenceDescriptor(
                    attribute_name="escrow_account_id",
                    strategy=lambda escrow_account: [escrow_account.entity_id.value]
                ),
            },
            Shipment: {
                Product: DomainReferenceDescriptor(
                    attribute_name="entity_id",
                    strategy=lambda order: [item.product_id.value for item in order.get_items()]
                ),
            },
            ShipmentSummary: {
                Product: DomainReferenceDescriptor(
                    attribute_name="entity_id",
                    strategy=lambda order: [item.product_id.value for item in order.get_items()]
                ),
            },
            Product: {},
        }
    
