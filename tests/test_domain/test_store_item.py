import copy
from typing import Callable
from domain.entity_id import EntityId
from domain.store_item import StoreItem
from domain.exceptions import NegativeAmountException
import pytest


def test_create_store_item(unique_id_factory: Callable[[], EntityId]) -> None:
    item = StoreItem(
        entity_id=unique_id_factory(),
        name="Potatoes red price", 
        amount=1, 
        store='Moscow', 
        price=1
    )
    assert item.name == "Potatoes red price"


def test_store_item_amount(potatoes_store_item_1: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_1()
    assert potatoes.amount == 1


def test_store_item_add_amount(potatoes_store_item_1: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_1()
    potatoes.amount += 1
    assert potatoes.amount == 2


def test_create_negative_amount_store_item(unique_id_factory: Callable[[], EntityId]) -> None:
    with pytest.raises(NegativeAmountException):
        store_item = StoreItem(
            entity_id=unique_id_factory(),
            name='potatoes', 
            amount=-1, 
            store='Moscow', 
            price=1
        )


def test_negative_amount_store_item(potatoes_store_item_1: Callable[[], StoreItem]) -> None:
    with pytest.raises(NegativeAmountException):
        store_item = potatoes_store_item_1()
        store_item.amount -= 5


def test_store_item_store(unique_id_factory: Callable[[], EntityId]) -> None:
    store_item = StoreItem(
        entity_id=unique_id_factory(),
        name='potatoes', 
        amount=10, 
        store='Moscow', 
        price=1
    )
    assert store_item.store == 'Moscow'


def test_store_item_price(unique_id_factory: Callable[[], EntityId]) -> None:
    potatoes = StoreItem(
        entity_id=unique_id_factory(),
        name='potatoes', 
        amount=10, 
        store='Moscow', 
        price=10
    )
    assert potatoes.price == 10


def test_eq(
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    potatoes = potatoes_store_item_10()
    same_potatoes = copy.deepcopy(potatoes)

    
    assert potatoes is not same_potatoes
    assert potatoes == same_potatoes


def test_not_eq(
    potatoes_store_item_10: Callable[[], StoreItem],
) -> None:
    potatoes = potatoes_store_item_10()
    not_same_potatoes = potatoes_store_item_10()
    
    assert potatoes != not_same_potatoes