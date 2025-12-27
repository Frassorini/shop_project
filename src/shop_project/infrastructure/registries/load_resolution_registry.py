from dataclasses import dataclass
from typing import Any, Callable, Generic, Type, TypeVar

from shop_project.application.entities.account import Account
from shop_project.application.entities.auth_session import AuthSession
from shop_project.application.entities.claim_token import ClaimToken
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

SourceType = TypeVar("SourceType")
TargetType = TypeVar("TargetType")


@dataclass(frozen=True)
class LoadResolutionDescriptor(Generic[SourceType]):
    attribute_name: str
    strategy: Callable[[SourceType], list[Any]]


_REGISTRY: dict[Type[Any], dict[Type[Any], LoadResolutionDescriptor[Any]]] = {
    ClaimToken: {
        Customer: LoadResolutionDescriptor(
            attribute_name="entity_id",
            strategy=lambda claim_token: [claim_token.entity_id],
        ),
    },
    Account: {
        Customer: LoadResolutionDescriptor(
            attribute_name="entity_id",
            strategy=lambda account: [account.entity_id],
        ),
        Employee: LoadResolutionDescriptor(
            attribute_name="entity_id",
            strategy=lambda account: [account.entity_id],
        ),
        Manager: LoadResolutionDescriptor(
            attribute_name="entity_id",
            strategy=lambda account: [account.entity_id],
        ),
    },
    AuthSession: {
        Customer: LoadResolutionDescriptor(
            attribute_name="entity_id",
            strategy=lambda auth_session: [auth_session.account_id],
        ),
        Employee: LoadResolutionDescriptor(
            attribute_name="entity_id",
            strategy=lambda auth_session: [auth_session.account_id],
        ),
        Manager: LoadResolutionDescriptor(
            attribute_name="entity_id",
            strategy=lambda auth_session: [auth_session.account_id],
        ),
    },
    Customer: {
        PurchaseActive: LoadResolutionDescriptor(
            attribute_name="customer_id",
            strategy=lambda customer: [customer.entity_id],
        ),
        PurchaseDraft: LoadResolutionDescriptor(
            attribute_name="customer_id",
            strategy=lambda customer: [customer.entity_id],
        ),
        PurchaseSummary: LoadResolutionDescriptor(
            attribute_name="customer_id",
            strategy=lambda customer: [customer.entity_id],
        ),
        EscrowAccount: LoadResolutionDescriptor(
            attribute_name="customer_id",
            strategy=lambda customer: [customer.entity_id],
        ),
    },
    PurchaseDraft: {
        Product: LoadResolutionDescriptor(
            attribute_name="entity_id",
            strategy=lambda cart: [item.product_id for item in cart.get_items()],
        ),
    },
    PurchaseActive: {
        Product: LoadResolutionDescriptor(
            attribute_name="entity_id",
            strategy=lambda order: [item.product_id for item in order.get_items()],
        ),
    },
    PurchaseSummary: {
        Product: LoadResolutionDescriptor(
            attribute_name="entity_id",
            strategy=lambda order: [item.product_id for item in order.get_items()],
        ),
    },
    EscrowAccount: {
        PurchaseActive: LoadResolutionDescriptor(
            attribute_name="escrow_account_id",
            strategy=lambda escrow_account: [escrow_account.entity_id],
        ),
        PurchaseSummary: LoadResolutionDescriptor(
            attribute_name="escrow_account_id",
            strategy=lambda escrow_account: [escrow_account.entity_id],
        ),
    },
    Shipment: {
        Product: LoadResolutionDescriptor(
            attribute_name="entity_id",
            strategy=lambda order: [item.product_id for item in order.get_items()],
        ),
    },
    ShipmentSummary: {
        Product: LoadResolutionDescriptor(
            attribute_name="entity_id",
            strategy=lambda order: [item.product_id for item in order.get_items()],
        ),
    },
    Product: {},
}


class DomainReferenceRegistry:

    @classmethod
    def get_reference_descriptor(
        cls, source_type: Type[SourceType], target_type: Type[TargetType]
    ) -> LoadResolutionDescriptor[SourceType]:
        if source_type not in cls._get_map():
            raise NotImplementedError(f"No descriptor for {source_type}")
        if target_type not in cls._get_map()[source_type]:
            raise NotImplementedError(
                f"No descriptor for {source_type} -> {target_type}"
            )

        return cls._get_map()[source_type][target_type]

    @classmethod
    def _get_map(
        cls,
    ) -> dict[Type[Any], dict[Type[Any], LoadResolutionDescriptor[Any]]]:
        return _REGISTRY
