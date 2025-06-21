from datetime import datetime, timezone
from itertools import count
from typing import Any, Callable, Type, TypeVar, cast

import pytest

from application.interfaces.p_repository import PRepository
from application.resource_loader.repository_container import RepositoryContainer
from application.resource_loader.resource_manager import ResourceManager
from domain.cart import Cart
from domain.customer import Customer
from domain.customer_order import CustomerOrder
from shared.entity_id import EntityId
from domain.store_item import StoreItem
from domain.supplier_order import SupplierOrder
from shared.entity_mixin import EntityMixin


pytest_plugins = [
    "tests.fixtures.fake_repository",
]


@pytest.fixture
def unique_id_factory() -> Callable[[], EntityId]:
    
    counter = count(start=1)
    
    def fact() -> EntityId:
        return EntityId(str(next(counter)))
    
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


DomainObject = TypeVar('DomainObject', 
                       Customer, 
                       CustomerOrder, 
                       SupplierOrder, 
                       Cart, 
                       StoreItem,)
@pytest.fixture
def domain_object_factory(customer_andrew: Callable[[], Customer],
                          customer_order_factory: Callable[[], CustomerOrder],
                          supplier_order_factory: Callable[[], SupplierOrder],
                          cart_factory: Callable[[], Cart],
                          potatoes_store_item_10: Callable[[], StoreItem]) -> Callable[[Type[DomainObject]], DomainObject]:
    def factory(model_type: Type[DomainObject]) -> DomainObject:
        if model_type is Customer:
            return cast(DomainObject, customer_andrew())
        elif model_type is CustomerOrder:
            return cast(DomainObject, customer_order_factory())
        elif model_type is SupplierOrder:
            return cast(DomainObject, supplier_order_factory())
        elif model_type is Cart:
            return cast(DomainObject, cart_factory())
        elif model_type is StoreItem:
            return cast(DomainObject, potatoes_store_item_10())
        else:
            raise ValueError(f'Unknown model type {model_type}')

    return factory

@pytest.fixture
def fake_repository_container_factory(
    fake_repository: Callable[[Type[Any], list[Any]], PRepository[Any]],
    ) -> Callable[[dict[Type[Any], list[Any]]], RepositoryContainer]:
    def factory(items_by_type: dict[Type[Any], list[Any]]) -> RepositoryContainer:
        repositories: dict[str, PRepository[Any]] = {
            "store_item": fake_repository(StoreItem, []),
            "customer_order": fake_repository(CustomerOrder, []),
        }
        
        type_arg_map: dict[Type[Any], str] = {
            StoreItem: "store_item",
            CustomerOrder: "customer_order",
        }
        
        for model_type, items in items_by_type.items():
            repositories[type_arg_map[model_type]] = fake_repository(model_type, items)
        
        return RepositoryContainer(**repositories) 
    
    return factory