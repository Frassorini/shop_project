from datetime import datetime, timezone
from itertools import count
from typing import Any, Callable
import pytest

from domain.customer import Customer
from domain.cart import Cart
from domain.customer_order import CustomerOrder
from domain.entity_id import EntityId
from domain.entity_mixin import EntityMixin
from domain.store_item import StoreItem
from domain.supplier_order import SupplierOrder

import pytest
from itertools import count
from typing import Callable


@pytest.fixture
def unique_id_factory() -> Callable[[], EntityId]:
    
    counter = count(start=1)
    
    def fact() -> EntityId:
        return EntityId(next(counter))
    
    return fact


@pytest.fixture
def store_item_factory(unique_id_factory: Callable[[], EntityId]) -> Callable[..., StoreItem]:
    
    def fact(*, name: str, 
             amount: float, 
             store: str, 
             price: float) -> StoreItem:

        return StoreItem(unique_id_factory(), name=name, amount=amount, store=store, price=price)
    
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


@pytest.fixture
def customer_andrew(unique_id_factory: Callable[[], EntityId]) -> Callable[[], Customer]:
    return lambda: Customer(unique_id_factory(), name='andrew')


@pytest.fixture
def customer_bob(unique_id_factory: Callable[[], EntityId]) -> Callable[[], Customer]:
    return lambda: Customer(unique_id_factory(), name='bob')


@pytest.fixture
def cart_factory(unique_id_factory: Callable[[], EntityId],
                 customer_andrew: Callable[[], Customer],) -> Callable[[], Cart]:
    def factory() -> Cart:
        cart = Cart(unique_id_factory(), customer_id=customer_andrew().entity_id, store='Moscow')
        return cart
    return factory


@pytest.fixture
def customer_order_factory(
    unique_id_factory: Callable[[], EntityId],
    customer_andrew: Callable[[], Customer],
) -> Callable[[], CustomerOrder]:
    def factory() -> CustomerOrder:
        order = CustomerOrder(entity_id=unique_id_factory(), customer_id=customer_andrew().entity_id, store='Moscow')
        return order
    return factory


@pytest.fixture
def supplier_order_factory(
    unique_id_factory: Callable[[], EntityId],
) -> Callable[[], SupplierOrder]:
    def factory() -> SupplierOrder:
        order = SupplierOrder(entity_id=unique_id_factory(), 
                              departure=datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc),
                              arrival=datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc), 
                              store="Moscow")
        return order
    return factory