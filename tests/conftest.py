from datetime import datetime, timezone
from itertools import count
from typing import Any, Callable
import pytest

from domain.cart_item import CartItem
from domain.customer import Customer
from domain.customer_order import CustomerOrder
from domain.customer_order_item import CustomerOrderItem
from domain.entity_id import EntityId
from domain.entity_mixin import EntityMixin
from domain.store_item import StoreItem
from domain.supplier_order_item import SupplierOrderItem
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
def customer_andrew_filled_cart(
    unique_id_factory: Callable[[], EntityId],
    customer_andrew: Callable[[], Customer],
    potatoes_store_item_10: Callable[[], StoreItem],
    sausages_store_item_10: Callable[[], StoreItem],
) -> Callable[[], Customer]:
    def factory() -> Customer:
        customer = customer_andrew()
        potatoes_cart = CartItem(unique_id_factory(), store_item=potatoes_store_item_10(), amount=5)
        sausages_cart = CartItem(unique_id_factory(), store_item=sausages_store_item_10(), amount=5)
        customer.cart += potatoes_cart
        customer.cart += sausages_cart
        return customer
    return factory


@pytest.fixture
def supplier_order_factory(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem],
) -> Callable[[], SupplierOrder]:
    def factory() -> SupplierOrder:
        potatoes = SupplierOrderItem(unique_id_factory(), store_item=potatoes_store_item_10(), amount=10)
        order = SupplierOrder(entity_id=unique_id_factory(), store='Moscow')
        order += potatoes
        return order
    return factory


@pytest.fixture
def customer_order_potatoes_10_factory(
    unique_id_factory: Callable[[], EntityId],
    customer_andrew: Callable[[], Customer],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> Callable[[], CustomerOrder]:
    def factory() -> CustomerOrder:
        store_item = potatoes_store_item_10()
        order_item = CustomerOrderItem(unique_id_factory(), store_item=store_item, amount=10)
        customer_order = CustomerOrder(unique_id_factory(), customer_andrew(), store='Moscow')
        customer_order += order_item
        return customer_order
    return factory
