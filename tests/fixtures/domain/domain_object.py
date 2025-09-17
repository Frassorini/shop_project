from typing import Any, Callable, Type, TypeVar, cast
from uuid import uuid4
from plum import overload, dispatch

import pytest

from shop_project.domain.store import Store
from shop_project.domain.cart import Cart
from shop_project.domain.customer import Customer
from shop_project.domain.customer_order import CustomerOrder
from shop_project.domain.store_item import StoreItem
from shop_project.domain.supplier_order import SupplierOrder
from shop_project.shared.entity_id import EntityId
from shop_project.domain.base_aggregate import BaseAggregate


@pytest.fixture
def domain_object_factory(customer_andrew: Callable[[], Customer],
                          customer_order_factory: Callable[[], CustomerOrder],
                          supplier_order_factory: Callable[[], SupplierOrder],
                          cart_factory: Callable[[], Cart],
                          potatoes_store_item_10: Callable[[], StoreItem],
                          store_factory: Callable[[str], Store]) -> Callable[[Type[BaseAggregate]], BaseAggregate]:
    def factory(model_type: Type[BaseAggregate]) -> BaseAggregate:
        if model_type is Customer:
            return cast(BaseAggregate, customer_andrew())
        elif model_type is CustomerOrder:
            return cast(BaseAggregate, customer_order_factory())
        elif model_type is SupplierOrder:
            return cast(BaseAggregate, supplier_order_factory())
        elif model_type is Cart:
            return cast(BaseAggregate, cart_factory())
        elif model_type is StoreItem:
            return cast(BaseAggregate, potatoes_store_item_10())
        elif model_type is Store:
            return cast(BaseAggregate, store_factory('Moscow'))
        else:
            raise ValueError(f'Unknown model type {model_type}')

    return factory

@pytest.fixture
def mutate_domain_object(customer_andrew: Callable[[], Customer],
                          customer_order_factory: Callable[[], CustomerOrder],
                          supplier_order_factory: Callable[[], SupplierOrder],
                          cart_factory: Callable[[], Cart],
                          potatoes_store_item_10: Callable[[], StoreItem],
                          store_factory: Callable[[str], Store]) -> Callable[[BaseAggregate], BaseAggregate]:
    @overload
    def _mutate_domain_object(domain_object: Customer) -> Customer:
        domain_object.name = 'bob'
        return domain_object

    @overload
    def _mutate_domain_object(domain_object: CustomerOrder) -> CustomerOrder:
        domain_object.store_id = EntityId(uuid4())
        return domain_object

    @overload
    def _mutate_domain_object(domain_object: SupplierOrder) -> SupplierOrder:
        domain_object.store_id = EntityId(uuid4())
        return domain_object

    @overload
    def _mutate_domain_object(domain_object: Cart) -> Cart:
        domain_object.store_id = EntityId(uuid4())
        return domain_object

    @overload
    def _mutate_domain_object(domain_object: StoreItem) -> StoreItem:
        domain_object.store_id = EntityId(uuid4())
        return domain_object

    @overload
    def _mutate_domain_object(domain_object: Store) -> Store:
        domain_object.name = 'New York' if domain_object.name == 'Moscow' else 'Moscow'
        return domain_object

    @overload
    def _mutate_domain_object(domain_object: BaseAggregate) -> BaseAggregate:
        raise ValueError(f'Unknown model type {type(domain_object)}')

    @dispatch
    def _mutate_domain_object(domain_object: Any) -> Any:
        pass

    return _mutate_domain_object
