from datetime import datetime, timezone
from itertools import count
from typing import Callable
import pytest

from domain.cart_item import CartItem
from domain.customer import Customer
from domain.customer_order import CustomerOrder
from domain.customer_order_item import CustomerOrderItem
from domain.domain_object import DomainObject
from domain.store_item import StoreItem
from domain.supplier_order_item import SupplierOrderItem
from domain.supplier_order import SupplierOrder


@pytest.fixture
def potatoes_store_item_1() -> StoreItem:
    return StoreItem(name='potatoes', amount=1, store='Moscow', price=1)


@pytest.fixture
def sausages_store_item_1() -> StoreItem:
    return StoreItem(name='sausages', amount=1, store='Moscow', price=1)


@pytest.fixture
def potatoes_store_item_1_another(potatoes_store_item_1: StoreItem) -> StoreItem:
    return potatoes_store_item_1


@pytest.fixture
def potatoes_store_item_10() -> StoreItem:
    return StoreItem(name='potatoes', amount=10, store='Moscow', price=1)


@pytest.fixture
def potatoes_store_item_10_petersburg() -> StoreItem:
    return StoreItem(name='potatoes', amount=10, store='Petersburg', price=1)


@pytest.fixture
def sausages_store_item_10() -> StoreItem:
    return StoreItem(name='sausages', amount=10, store='Moscow', price=1)


@pytest.fixture
def customer_andrew() -> Customer:
    andrew = Customer(name='andrew')
    andrew.id_ = 1
    return andrew


@pytest.fixture
def customer_bob() -> Customer:
    bob = Customer(name='bob')
    bob.id_ = 2
    return bob


@pytest.fixture
def customer_andrew_filled_cart(customer_andrew: Customer, 
                                potatoes_store_item_10: StoreItem, 
                                sausages_store_item_10: StoreItem) -> Customer:
    potatoes_cart = CartItem(store_item=potatoes_store_item_10, amount=5)
    sausages_cart = CartItem(store_item=sausages_store_item_10, amount=5)
    customer_andrew.cart += potatoes_cart
    customer_andrew.cart += sausages_cart
    return customer_andrew


@pytest.fixture
def supplier_order(potatoes_store_item_10: StoreItem) -> SupplierOrder:
    potatoes = SupplierOrderItem(store_item=potatoes_store_item_10, amount=10)
    order = SupplierOrder(store='Moscow')
    order += potatoes
    return order


@pytest.fixture
def customer_order_potatoes_10_factory(customer_andrew: Customer) -> Callable[[], CustomerOrder]:
    counter = count(start=1)
    def factory() -> CustomerOrder:
        store_item = StoreItem(name='potatoes', amount=10, store='Moscow', price=1)
        store_item.id_ = next(counter)
        order_item = CustomerOrderItem(store_item=store_item, amount=10)
        order_item.id_ = next(counter)
        customer_order = CustomerOrder(customer_andrew, store='Moscow')
        customer_order += order_item
        return customer_order
    return factory