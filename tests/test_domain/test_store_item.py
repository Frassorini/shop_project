import copy
from domain.store_item import StoreItem
from domain.exceptions import NegativeAmountException
import pytest


def test_create_store_item() -> None:
    item = StoreItem(name="Potatoes red price", amount=1, store='Moscow', price=1)
    assert item.name == "Potatoes red price"


def test_store_item_amount(potatoes_store_item_1: StoreItem) -> None:
    potatoes = potatoes_store_item_1
    assert potatoes.amount == 1


def test_store_item_add_amount(potatoes_store_item_1: StoreItem) -> None:
    potatoes = potatoes_store_item_1
    
    potatoes.amount += 1
    
    assert potatoes.amount == 2


def test_create_negative_amount_store_item() -> None:
    with pytest.raises(NegativeAmountException):
        store_item = StoreItem('potatoes', amount=-1, store='Moscow', price=1)


def test_negative_amount_store_item(potatoes_store_item_1: StoreItem) -> None:
    with pytest.raises(NegativeAmountException):
        store_item = potatoes_store_item_1
        store_item.amount -= 5


def test_store_item_store() -> None:
    store_item = StoreItem(name='potatoes', amount=10, store='Moscow', price=1)
    
    assert store_item.store == 'Moscow'


def test_store_item_price() -> None:
    potatoes = StoreItem(name='potatoes', amount=10, store='Moscow', price=10)
    
    assert potatoes.price == 10


def test_eq(potatoes_store_item_10: StoreItem) -> None:
    same_potatoes = copy.deepcopy(potatoes_store_item_10)
    potatoes_store_item_10.id_ = 1
    same_potatoes.id_ = 1
    
    assert potatoes_store_item_10 is not same_potatoes
    assert potatoes_store_item_10 == same_potatoes


def test_not_eq(potatoes_store_item_10: StoreItem) -> None:
    not_same_potatoes = copy.deepcopy(potatoes_store_item_10)
    potatoes_store_item_10.id_ = 1
    not_same_potatoes.id_ = 2
    
    assert potatoes_store_item_10 != not_same_potatoes