from typing import Callable, Type, TypeVar, cast

import pytest

from domain.store import Store
from domain.cart import Cart
from domain.customer import Customer
from domain.customer_order import CustomerOrder
from domain.store_item import StoreItem
from domain.supplier_order import SupplierOrder


DomainObject = TypeVar('DomainObject')
@pytest.fixture
def domain_object_factory(customer_andrew: Callable[[], Customer],
                          customer_order_factory: Callable[[], CustomerOrder],
                          supplier_order_factory: Callable[[], SupplierOrder],
                          cart_factory: Callable[[], Cart],
                          potatoes_store_item_10: Callable[[], StoreItem],
                          store_factory: Callable[[str], Store]) -> Callable[[Type[DomainObject]], DomainObject]:
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
        elif model_type is Store:
            return cast(DomainObject, store_factory('Moscow'))
        else:
            raise ValueError(f'Unknown model type {model_type}')

    return factory


@pytest.fixture
def mutate_domain_object(
    store_factory_with_cache: Callable[[str], Store],
    ) -> Callable[[DomainObject], DomainObject]:
    def factory(domain_object: DomainObject) -> DomainObject:
        store_obj: Store = store_factory_with_cache('Moscow')
        if isinstance(domain_object, Customer):
            domain_object.name = 'bob'
        elif isinstance(domain_object, CustomerOrder):
            domain_object.store_id = store_obj.entity_id
        elif isinstance(domain_object, SupplierOrder):
            domain_object.store_id = store_obj.entity_id
        elif isinstance(domain_object, Cart):
            domain_object.store_id = store_obj.entity_id
        elif isinstance(domain_object, StoreItem):
            domain_object.store_id = store_obj.entity_id
        elif isinstance(domain_object, Store):
            domain_object.name = 'New York' if domain_object.name == 'Moscow' else 'Moscow'
        else:
            raise ValueError(f'Unknown model type {type(domain_object)}')
        
        return domain_object
    return factory