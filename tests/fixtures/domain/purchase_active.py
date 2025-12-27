from typing import Callable, cast

import pytest
from dishka.container import Container

from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.purchase_activation_service import (
    PurchaseActivation,
    PurchaseActivationService,
)
from tests.helpers import AggregateContainer


@pytest.fixture
def purchase_active_filled_factory(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    domain_container: Container,
) -> Callable[[], PurchaseActivation]:
    def factory() -> PurchaseActivation:
        purchase_activation_service = domain_container.get(PurchaseActivationService)

        purchase_draft = purchase_draft_factory()
        potatoes = potatoes_product_10()
        sausages = sausages_product_10()
        purchase_draft.add_item(potatoes.entity_id, 10)
        purchase_draft.add_item(sausages.entity_id, 10)

        product_inventory = ProductInventory(stock=[potatoes, sausages])

        purchase_activation = purchase_activation_service.activate(
            product_inventory, purchase_draft
        )

        return purchase_activation

    return factory


@pytest.fixture
def purchase_active_filled_container_factory(
    purchase_draft_container_factory: Callable[[], AggregateContainer],
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    domain_container: Container,
) -> Callable[[], AggregateContainer]:
    def factory() -> AggregateContainer:
        purchase_activation_service = domain_container.get(PurchaseActivationService)

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

        container: AggregateContainer = AggregateContainer(
            aggregate=purchase_activation.purchase_active,
            dependencies={
                EscrowAccount: [purchase_activation.escrow_account],
                Product: [potatoes, sausages],
            },
        )
        container.merge(purchase_draft_container)

        return container

    return factory


@pytest.fixture
def escrow_account_container_factory(
    purchase_active_filled_container_factory: Callable[[], AggregateContainer],
) -> Callable[[], AggregateContainer]:
    def factory() -> AggregateContainer:
        purchase_container = purchase_active_filled_container_factory()

        container = AggregateContainer(
            purchase_container.dependencies[EscrowAccount][0], dependencies={}
        )
        container.merge(purchase_container)
        container.dependencies[PurchaseActive].pop(0)

        return container

    return factory
