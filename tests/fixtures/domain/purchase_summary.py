from typing import Callable, cast

import pytest
from dishka.container import Container

from shop_project.application.entities.account import Account
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.purchase_activation_service import (
    PurchaseActivationService,
)
from shop_project.domain.services.purchase_claim_service import PurchaseClaimService
from tests.helpers import AggregateContainer


@pytest.fixture
def purchase_summary_filled_container_factory(
    purchase_draft_container_factory: Callable[[], AggregateContainer],
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    employee_container_factory: Callable[[], AggregateContainer],
    domain_container: Container,
) -> Callable[[], AggregateContainer]:
    def factory() -> AggregateContainer:
        employee_container = employee_container_factory()
        employee: Employee = (
            employee_container.aggregate
        )  # pyright: ignore[reportAssignmentType]
        employee.authorize()
        purchase_activation_service = domain_container.get(PurchaseActivationService)
        purchase_claim_service = domain_container.get(PurchaseClaimService)

        purchase_draft_container = purchase_draft_container_factory()
        purchase_draft: PurchaseDraft = cast(
            PurchaseDraft, purchase_draft_container.aggregate
        )
        potatoes = potatoes_product_10()
        sausages = sausages_product_10()
        purchase_draft.add_item(potatoes.entity_id, 10)
        purchase_draft.add_item(sausages.entity_id, 10)

        product_inventory = ProductInventory(stock=[potatoes, sausages])

        purchase_activation = purchase_activation_service.activate(
            product_inventory, purchase_draft
        )

        purchase_active = purchase_activation.purchase_active
        escrow = purchase_activation.escrow_account

        escrow.mark_as_paid()

        purchase_summary = purchase_claim_service.claim(
            employee, purchase_active, escrow
        )

        container: AggregateContainer = AggregateContainer(
            aggregate=purchase_summary,
            dependencies={
                EscrowAccount: [escrow],
                Product: [potatoes, sausages],
                Customer: [purchase_draft_container.dependencies[Customer][0]],
                Account: [purchase_draft_container.dependencies[Account][0]],
            },
        )

        container.merge(employee_container)

        return container

    return factory
