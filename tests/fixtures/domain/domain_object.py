from typing import Callable, Type

import pytest

from shop_project.application.entities.account import Account
from shop_project.application.entities.auth_session import AuthSession
from shop_project.application.entities.claim_token import ClaimToken
from shop_project.application.entities.external_id_totp import ExternalIdTotp
from shop_project.application.entities.task import Task
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.manager import Manager
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.domain.entities.shipment import Shipment
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from tests.helpers import AggregateContainer


@pytest.fixture
def domain_object_factory(
    task_container_factory: Callable[..., AggregateContainer],
    claim_token_container_factory: Callable[..., AggregateContainer],
    account_container_factory: Callable[..., AggregateContainer],
    external_id_totp_container_factory: Callable[..., AggregateContainer],
    auth_session_container_factory: Callable[..., AggregateContainer],
    manager_container_factory: Callable[..., AggregateContainer],
    employee_container_factory: Callable[..., AggregateContainer],
    customer_container_factory: Callable[..., AggregateContainer],
    escrow_account_container_factory: Callable[..., AggregateContainer],
    purchase_active_filled_container_factory: Callable[[], AggregateContainer],
    purchase_summary_filled_container_factory: Callable[[], AggregateContainer],
    shipment_container_factory: Callable[[], AggregateContainer],
    purchase_draft_container_factory: Callable[[], AggregateContainer],
    product_container_factory: Callable[..., AggregateContainer],
) -> Callable[[Type[PersistableEntity]], AggregateContainer]:
    def factory(model_type: Type[PersistableEntity]) -> AggregateContainer:
        if model_type is Task:
            return task_container_factory()
        if model_type is ClaimToken:
            return claim_token_container_factory()
        if model_type is Account:
            return account_container_factory()
        if model_type is ExternalIdTotp:
            return external_id_totp_container_factory()
        if model_type is AuthSession:
            return auth_session_container_factory()
        if model_type is Manager:
            return manager_container_factory()
        if model_type is Employee:
            return employee_container_factory()
        elif model_type is Customer:
            return customer_container_factory()
        elif model_type is EscrowAccount:
            return escrow_account_container_factory()
        elif model_type is PurchaseActive:
            return purchase_active_filled_container_factory()
        elif model_type is PurchaseSummary:
            return purchase_summary_filled_container_factory()
        elif model_type is Shipment:
            return shipment_container_factory()
        elif model_type is PurchaseDraft:
            return purchase_draft_container_factory()
        elif model_type is Product:
            return product_container_factory(name="potatoes", amount=1, price=1)
        else:
            raise ValueError(f"Unknown model type {model_type}")

    return factory
