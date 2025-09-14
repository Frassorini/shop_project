from decimal import Decimal
from typing import Callable

import pytest

from shop_project.domain.store import Store
from shop_project.shared.entity_id import EntityId
from shop_project.domain.store_item import StoreItem


@pytest.fixture
def store_factory(unique_id_factory: Callable[[], EntityId]) -> Callable[[str], Store]:
    
    def fact(name: str) -> Store:
        return Store(unique_id_factory(), name=name)
    
    return fact


@pytest.fixture
def store_factory_with_cache(unique_id_factory: Callable[[], EntityId]) -> Callable[[str], Store]:
    cache: dict[str, Store] = {}

    def factory(name: str) -> Store:
        if name in cache:
            return cache[name]
        
        store = Store(unique_id_factory(), name=name)
        cache[name] = store
        return store
    
    return factory


@pytest.fixture
def store_item_factory(unique_id_factory: Callable[[], EntityId],
                       store_factory_with_cache: Callable[[str], Store]) -> Callable[..., StoreItem]:
    
    def fact(*, name: str, 
             amount: float, 
             store: str, 
             price: Decimal) -> StoreItem:

        store_obj: Store = store_factory_with_cache(store)

        return StoreItem(unique_id_factory(), name=name, amount=amount, store_id=store_obj.entity_id, price=price)
    
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