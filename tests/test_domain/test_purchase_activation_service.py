from typing import Callable

import pytest
from dishka.container import Container

from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.exceptions import DomainException
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.purchase_activation_service import (
    PurchaseActivationService,
)


def test_activate(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
    domain_container: Container,
) -> None:
    purchase_activation_service = domain_container.get(PurchaseActivationService)

    potatoes = potatoes_product_10()
    purchase_draft = purchase_draft_factory()
    purchase_draft.add_item(product_id=potatoes.entity_id, amount=2)
    product_inventory = ProductInventory([potatoes])

    activation = purchase_activation_service.activate(product_inventory, purchase_draft)

    assert potatoes.amount == 8
    assert activation.escrow_account.is_pending()
    assert activation.purchase_active.get_items()[0].amount == 2


def test_activate_twice(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
    domain_container: Container,
) -> None:
    purchase_activation_service = domain_container.get(PurchaseActivationService)

    potatoes = potatoes_product_10()
    purchase_draft = purchase_draft_factory()
    purchase_draft.add_item(product_id=potatoes.entity_id, amount=2)
    product_inventory = ProductInventory([potatoes])

    activation = purchase_activation_service.activate(product_inventory, purchase_draft)

    with pytest.raises(DomainException):
        purchase_activation_service.activate(product_inventory, purchase_draft)
