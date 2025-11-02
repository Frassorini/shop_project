from typing import Callable
import pytest

from shop_project.domain.exceptions import DomainException
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.services.purchase_activation_service import PurchaseActivationService
from shop_project.domain.product_inventory import ProductInventory
from shop_project.domain.product import Product
from shop_project.domain.purchase_active import PurchaseActive


def test_(potatoes_product_10: Callable[[], Product], 
          purchase_activation_service_factory: Callable[[], PurchaseActivationService]) -> None:
    potatoes = potatoes_product_10()
    product_inventory = ProductInventory([potatoes])
    purchase_activation_service = purchase_activation_service_factory()


def test_activate(purchase_draft_factory: Callable[[], PurchaseDraft],
                  potatoes_product_10: Callable[[], Product],
                  purchase_activation_service_factory: Callable[[], PurchaseActivationService]) -> None:
    potatoes = potatoes_product_10()
    purchase_draft = purchase_draft_factory()
    purchase_draft.add_item(product_id=potatoes.entity_id, amount=2)
    product_inventory = ProductInventory([potatoes])
    purchase_activation_service = purchase_activation_service_factory()

    activation = purchase_activation_service.activate(product_inventory, purchase_draft)

    assert potatoes.amount == 8
    assert activation.escrow_account.is_pending()
    assert activation.purchase_active.get_items()[0].amount == 2


def test_activate_twice(purchase_draft_factory: Callable[[], PurchaseDraft],
                              potatoes_product_10: Callable[[], Product],
                              purchase_activation_service_factory: Callable[[], PurchaseActivationService]) -> None:
    potatoes = potatoes_product_10()
    purchase_draft = purchase_draft_factory()
    purchase_draft.add_item(product_id=potatoes.entity_id, amount=2)
    product_inventory = ProductInventory([potatoes])
    purchase_activation_service = purchase_activation_service_factory()
    
    activation = purchase_activation_service.activate(product_inventory, purchase_draft)

    with pytest.raises(DomainException):
        purchase_activation_service.activate(product_inventory, purchase_draft)
