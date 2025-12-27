from typing import Callable
from uuid import uuid4

import pytest

from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_draft import PurchaseDraft, PurchaseDraftItem
from shop_project.domain.exceptions import DomainException


def test_add_item(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
) -> None:
    cart = purchase_draft_factory()
    product: Product = potatoes_product_10()

    cart.add_item(product_id=product.entity_id, amount=2)


def test_add_negative_amount(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
) -> None:
    cart = purchase_draft_factory()
    product: Product = potatoes_product_10()

    with pytest.raises(DomainException):
        cart.add_item(product_id=product.entity_id, amount=-2)


def test_get_item(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
) -> None:
    product: Product = potatoes_product_10()
    cart = purchase_draft_factory()

    cart.add_item(product_id=product.entity_id, amount=2)

    cart_item: PurchaseDraftItem = cart.get_item(product.entity_id)

    assert cart_item.amount == 2


def test_add_duplicate_item(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
) -> None:
    product: Product = potatoes_product_10()
    cart = purchase_draft_factory()

    cart.add_item(product_id=product.entity_id, amount=2)
    cart.add_item(product_id=product.entity_id, amount=3)

    assert cart.get_item(product.entity_id).amount == 5


def test_remove_item_and_get_not_existent(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
) -> None:
    product: Product = potatoes_product_10()
    cart = purchase_draft_factory()

    cart.add_item(product_id=product.entity_id, amount=2)
    cart.remove_item(product.entity_id)

    with pytest.raises(DomainException):
        cart.get_item(product.entity_id)


def test_in(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
) -> None:
    product: Product = potatoes_product_10()
    cart = purchase_draft_factory()

    cart.add_item(product_id=product.entity_id, amount=2)

    assert product.entity_id in cart
    assert uuid4() not in cart


def test_add_too_many_products(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
) -> None:
    product: Product = potatoes_product_10()
    cart = purchase_draft_factory()

    with pytest.raises(DomainException):
        for i in range(41):
            cart.add_item(product_id=uuid4(), amount=1)
