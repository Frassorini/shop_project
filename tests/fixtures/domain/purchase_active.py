from typing import Callable

import pytest

from shop_project.domain.customer import Customer
from shop_project.domain.escrow_account import EscrowAccount
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.services.inventory_service import InventoryService
from shop_project.domain.services.checkout_service import CheckoutService
from shop_project.domain.services.purchase_activation_service import PurchaseActivationService, PurchaseActivation
from shop_project.domain.services.purchase_reservation_service import PurchaseReservationService
from shop_project.domain.product import Product
from shop_project.shared.entity_id import EntityId

from tests.helpers import AggregateContainer


@pytest.fixture
def purchase_active_filled_factory(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    purchase_activation_service_factory: Callable[[InventoryService], PurchaseActivationService],
) -> Callable[[], PurchaseActivation]:
    def factory() -> PurchaseActivation:
        purchase_draft = purchase_draft_factory()
        potatoes = potatoes_product_10()
        sausages = sausages_product_10()
        purchase_draft.add_item(potatoes.entity_id, 10)
        purchase_draft.add_item(sausages.entity_id, 10)
        
        inventory_service = InventoryService(stock=[potatoes, sausages])
        purchase_activation_service = purchase_activation_service_factory(inventory_service)
        
        purchase_activation = purchase_activation_service.activate(purchase_draft)
        
        return purchase_activation
    return factory


@pytest.fixture
def purchase_active_filled_container_factory(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    purchase_activation_service_factory: Callable[[InventoryService], PurchaseActivationService],
) -> Callable[[], AggregateContainer]:
    def factory() -> AggregateContainer:
        purchase_draft = purchase_draft_factory()
        potatoes = potatoes_product_10()
        sausages = sausages_product_10()
        purchase_draft.add_item(potatoes.entity_id, 10)
        purchase_draft.add_item(sausages.entity_id, 10)
        
        inventory_service = InventoryService(stock=[potatoes, sausages])
        purchase_activation_service = purchase_activation_service_factory(inventory_service)
        
        purchase_activation = purchase_activation_service.activate(purchase_draft)
        
        container: AggregateContainer = AggregateContainer(
            aggregate=purchase_activation.purchase_active, 
            dependencies={EscrowAccount: [purchase_activation.escrow_account],
                          Product: [potatoes, sausages]})
        
        return container
    return factory


# @pytest.fixture
# def customer_order_container_factory(
#     unique_id_factory: Callable[[], EntityId],
#     customer_andrew: Callable[[], Customer],
#     product_container_factory: Callable[..., AggregateContainer],
# ) -> Callable[[], AggregateContainer]:
#     def factory() -> AggregateContainer:
#         customer = customer_andrew()
#         order = PurchaseActive(entity_id=unique_id_factory(), customer_id=customer.entity_id)
#         product = product_container_factory(name='potatoes', amount=1, price=1).aggregate
        
#         container: AggregateContainer = AggregateContainer(
#             aggregate=order, 
#             dependencies={Customer: [customer], 
#                           Product: [product],})
        
#         return container
#     return factory
