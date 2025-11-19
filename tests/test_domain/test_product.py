import copy
from decimal import Decimal
from typing import Callable

import pytest

from shop_project.domain.entities.product import Product
from shop_project.domain.exceptions import DomainException, NegativeAmountException
from shop_project.shared.entity_id import EntityId


def test_snapshot(unique_id_factory: Callable[[], EntityId]) -> None:
    item = Product(
        entity_id=unique_id_factory(), name="potatoes", amount=1, price=Decimal(1)
    )
    assert item.to_dict() == {
        "entity_id": item.entity_id.value,
        "name": "potatoes",
        "amount": 1,
        "price": Decimal(1),
    }


def test_from_snapshot(unique_id_factory: Callable[[], EntityId]) -> None:
    item = Product.from_dict(
        {
            "entity_id": unique_id_factory().value,
            "name": "potatoes",
            "amount": 1,
            "price": Decimal(1),
        }
    )
    assert item.name == "potatoes"


def test_product_amount(potatoes_product_1: Callable[[], Product]) -> None:
    potatoes = potatoes_product_1()
    assert potatoes.amount == 1


def test_product_add_amount(potatoes_product_1: Callable[[], Product]) -> None:
    potatoes = potatoes_product_1()
    potatoes.amount += 1
    assert potatoes.amount == 2


def test_create_negative_amount_product(
    unique_id_factory: Callable[[], EntityId],
) -> None:
    with pytest.raises(NegativeAmountException):
        product = Product(
            entity_id=unique_id_factory(), name="potatoes", amount=-1, price=Decimal(1)
        )


def test_negative_amount_product(potatoes_product_1: Callable[[], Product]) -> None:
    product = potatoes_product_1()
    with pytest.raises(NegativeAmountException):
        product.amount -= 5


def test_eq(potatoes_product_10: Callable[[], Product]) -> None:
    potatoes = potatoes_product_10()
    same_potatoes = copy.deepcopy(potatoes)

    assert potatoes is not same_potatoes
    assert potatoes == same_potatoes


def test_not_eq(
    potatoes_product_10: Callable[[], Product],
) -> None:
    potatoes = potatoes_product_10()
    not_same_potatoes = potatoes_product_10()

    assert potatoes != not_same_potatoes


def test_reserve(potatoes_product_10: Callable[[], Product]) -> None:
    potatoes = potatoes_product_10()

    potatoes.reserve(4)

    assert potatoes.amount == 6


def test_reserve_insufficient(potatoes_product_10: Callable[[], Product]) -> None:
    potatoes = potatoes_product_10()

    with pytest.raises(DomainException):
        potatoes.reserve(11)


def test_restock(potatoes_product_10: Callable[[], Product]) -> None:
    potatoes = potatoes_product_10()

    potatoes.restock(4)

    assert potatoes.amount == 14
