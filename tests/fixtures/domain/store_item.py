from decimal import Decimal
from typing import Callable

import pytest

from shop_project.shared.entity_id import EntityId
from shop_project.domain.store_item import StoreItem
from tests.helpers import AggregateContainer


@pytest.fixture
def store_item_factory(unique_id_factory: Callable[[], EntityId]) -> Callable[..., StoreItem]:
    
    def fact(*, name: str, 
             amount: int, 
             price: Decimal) -> StoreItem:

        return StoreItem(unique_id_factory(), name=name, amount=amount, price=price)
    
    return fact


@pytest.fixture
def store_item_container_factory(unique_id_factory: Callable[[], EntityId]) -> Callable[..., AggregateContainer]:
    
    def fact(*, name: str, 
             amount: int, 
             price: Decimal) -> AggregateContainer:

        store_item = StoreItem(unique_id_factory(), name=name, amount=amount, price=price)

        return AggregateContainer(aggregate=store_item, dependencies={})
    
    return fact


@pytest.fixture
def potatoes_store_item_1(store_item_factory: Callable[..., StoreItem]) -> Callable[[], StoreItem]:
    
    def fact(*, price: float | None = None) -> StoreItem:
        if price is None:
            price = 1

        return store_item_factory(name='potatoes', amount=1, price=price)
    
    return fact


@pytest.fixture
def potatoes_store_item_10(store_item_factory: Callable[..., StoreItem]) -> Callable[[], StoreItem]:
    
    def fact(*, price: float | None = None) -> StoreItem:
        if price is None:
            price = 1

        return store_item_factory(name='potatoes', amount=10, price=price)
    
    return fact


@pytest.fixture
def sausages_store_item_1(store_item_factory: Callable[..., StoreItem]) -> Callable[[], StoreItem]:
    
    def fact(*, price: float | None = None) -> StoreItem:
        if price is None:
            price = 1

        return store_item_factory(name='sausages', amount=1, price=price)
    
    return fact


@pytest.fixture
def sausages_store_item_10(store_item_factory: Callable[..., StoreItem]) -> Callable[[], StoreItem]:
    
    def fact(*, price: float | None = None) -> StoreItem:
        if price is None:
            price = 1

        return store_item_factory(name='sausages', amount=10, price=price)
    
    return fact