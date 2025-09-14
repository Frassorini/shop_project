import copy
from decimal import Decimal
from typing import Callable
from shop_project.domain.store import Store
from shop_project.shared.entity_id import EntityId
from shop_project.domain.store_item import StoreItem
from shop_project.domain.exceptions import DomainException, NegativeAmountException
import pytest


def test_snapshot(unique_id_factory: Callable[[], EntityId]) -> None:
    item = StoreItem(
        entity_id=unique_id_factory(),
        name="potatoes", 
        amount=1, 
        store_id=unique_id_factory(), 
        price=Decimal(1)
    )
    assert item.to_dict() == {'entity_id': item.entity_id.value, 'name': 'potatoes', 'amount': 1, 'store_id': item.store_id.value, 'price': Decimal(1)}


def test_from_snapshot(unique_id_factory: Callable[[], EntityId]) -> None:
    item = StoreItem.from_dict({
        'entity_id': unique_id_factory().value,
        'name': 'potatoes',
        'amount': 1,
        'store_id': unique_id_factory().value,
        'price': Decimal(1)
        })
    assert item.name == 'potatoes'


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
            store_id=unique_id_factory(), 
            price=Decimal(1)
        )


def test_negative_amount_store_item(potatoes_store_item_1: Callable[[], StoreItem]) -> None:
    store_item = potatoes_store_item_1()
    with pytest.raises(NegativeAmountException):
        store_item.amount -= 5


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


def test_reserve(potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_10()
    
    potatoes.reserve(4)
    
    assert potatoes.amount == 6
    

def test_reserve_insufficient(potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_10()
    
    with pytest.raises(DomainException):
        potatoes.reserve(11)


def test_restock(potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_10()
    
    potatoes.restock(4)
    
    assert potatoes.amount == 14