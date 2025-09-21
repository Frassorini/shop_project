from decimal import Decimal
from typing import Callable

import pytest

from shop_project.domain.store import Store
from shop_project.shared.entity_id import EntityId
from shop_project.domain.store_item import StoreItem
from tests.helpers import AggregateContainer


@pytest.fixture
def store_item_factory(unique_id_factory: Callable[[], EntityId],
                       store_factory_with_cache: Callable[[str], Store]) -> Callable[..., StoreItem]:
    
    def fact(*, name: str, 
             amount: int, 
             store: str, 
             price: Decimal) -> StoreItem:

        store_obj: Store = store_factory_with_cache(store)

        return StoreItem(unique_id_factory(), name=name, amount=amount, store_id=store_obj.entity_id, price=price)
    
    return fact


@pytest.fixture
def store_item_container_factory(unique_id_factory: Callable[[], EntityId]) -> Callable[..., AggregateContainer]:
    
    def fact(*, name: str, 
             amount: int, 
             store: Store, 
             price: Decimal) -> AggregateContainer:

        store_item = StoreItem(unique_id_factory(), name=name, amount=amount, store_id=store.entity_id, price=price)

        return AggregateContainer(aggregate=store_item, dependencies={Store: [store]})
    
    return fact


@pytest.fixture
def potatoes_store_item_1(store_item_factory: Callable[..., StoreItem]) -> Callable[[], StoreItem]:
    
    def fact(*, store: str | None = None, 
             price: float | None = None) -> StoreItem:
        if store is None:
            store = 'Moscow'
        if price is None:
            price = 1

        return store_item_factory(name='potatoes', amount=1, store=store, price=price)
    
    return fact


@pytest.fixture
def potatoes_store_item_10(store_item_factory: Callable[..., StoreItem]) -> Callable[[], StoreItem]:
    
    def fact(*, store: str | None = None, 
             price: float | None = None) -> StoreItem:
        if store is None:
            store = 'Moscow'
        if price is None:
            price = 1

        return store_item_factory(name='potatoes', amount=10, store=store, price=price)
    
    return fact


@pytest.fixture
def sausages_store_item_1(store_item_factory: Callable[..., StoreItem]) -> Callable[[], StoreItem]:
    
    def fact(*, store: str | None = None, 
             price: float | None = None) -> StoreItem:
        if store is None:
            store = 'Moscow'
        if price is None:
            price = 1

        return store_item_factory(name='sausages', amount=1, store=store, price=price)
    
    return fact


@pytest.fixture
def sausages_store_item_10(store_item_factory: Callable[..., StoreItem]) -> Callable[[], StoreItem]:
    
    def fact(*, store: str | None = None, 
             price: float | None = None) -> StoreItem:
        if store is None:
            store = 'Moscow'
        if price is None:
            price = 1

        return store_item_factory(name='sausages', amount=10, store=store, price=price)
    
    return fact