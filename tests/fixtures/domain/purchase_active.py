from typing import Callable

import pytest

from dishka.container import Container

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.checkout_service import CheckoutService
from shop_project.domain.services.purchase_activation_service import PurchaseActivationService, PurchaseActivation
from shop_project.domain.services.purchase_reservation_service import PurchaseReservationService
from shop_project.domain.entities.product import Product
from shop_project.shared.entity_id import EntityId

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
        
        purchase_activation = purchase_activation_service.activate(product_inventory, purchase_draft)
        
        return purchase_activation
    return factory


@pytest.fixture
def purchase_active_filled_container_factory(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    domain_container: Container,
) -> Callable[[], AggregateContainer]:
    def factory() -> AggregateContainer:
        purchase_activation_service = domain_container.get(PurchaseActivationService)
        
        purchase_draft = purchase_draft_factory()
        potatoes = potatoes_product_10()
        sausages = sausages_product_10()
        purchase_draft.add_item(potatoes.entity_id, 10)
        purchase_draft.add_item(sausages.entity_id, 10)
        
        product_inventory = ProductInventory(stock=[potatoes, sausages])
        
        purchase_activation = purchase_activation_service.activate(product_inventory, purchase_draft)
        
        container: AggregateContainer = AggregateContainer(
            aggregate=purchase_activation.purchase_active, 
            dependencies={EscrowAccount: [purchase_activation.escrow_account],
                          Product: [potatoes, sausages]})
        
        return container
    return factory
