from dataclasses import dataclass
from typing import Any, Callable, Generic, Type, TypeVar

from domain.cart import Cart
from domain.customer import Customer
from domain.customer_order import CustomerOrder
from domain.store_item import StoreItem
from domain.supplier_order import SupplierOrder
from domain.store import Store


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
                CustomerOrder: DomainReferenceDescriptor(
                    attribute_name="customer_id",
                    strategy=lambda customer: [customer.entity_id]
                ),
                Cart: DomainReferenceDescriptor(
                    attribute_name="entity_id",
                    strategy=lambda customer: [customer.entity_id]
                ),
            },
            CustomerOrder: {
                StoreItem: DomainReferenceDescriptor(
                    attribute_name="entity_id",
                    strategy=lambda order: [item.store_item_id for item in order.get_items()],
                ),
                Store: DomainReferenceDescriptor(
                    attribute_name="store_id",
                    strategy=lambda order: [order.store_id],
                )
            },
            SupplierOrder: {
                StoreItem: DomainReferenceDescriptor(
                    attribute_name="entity_id",
                    strategy=lambda order: [item.store_item_id for item in order.get_items()]
                ),
            },
            Cart: {
                StoreItem: DomainReferenceDescriptor(
                    attribute_name="entity_id",
                    strategy=lambda cart: [item.store_item_id for item in cart.get_items()]
                ),
            },
            StoreItem: {},
            Store: {},
        }
    
