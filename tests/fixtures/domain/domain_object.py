from os import name
from typing import Any, Callable, Type, TypeVar, cast
from uuid import uuid4
from plum import overload, dispatch

import pytest

from shop_project.domain.store import Store
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.customer import Customer
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.store_item import StoreItem
from shop_project.domain.supplier_order import SupplierOrder
from shop_project.shared.entity_id import EntityId
from shop_project.domain.base_aggregate import BaseAggregate

from tests.helpers import AggregateContainer


@pytest.fixture
def domain_object_factory(customer_andrew: Callable[[], Customer],
                          customer_order_container_factory: Callable[[], AggregateContainer],
                          supplier_order_container_factory: Callable[[], AggregateContainer],
                          cart_container_factory: Callable[[], AggregateContainer],
                          store_item_container_factory: Callable[..., AggregateContainer],
                          store_factory: Callable[[str], Store]) -> Callable[[Type[BaseAggregate]], AggregateContainer]:
    def factory(model_type: Type[BaseAggregate]) -> AggregateContainer:
        if model_type is Customer:
            return AggregateContainer(customer_andrew(), dependencies={})
        elif model_type is PurchaseActive:
            return customer_order_container_factory()
        elif model_type is SupplierOrder:
            return supplier_order_container_factory()
        elif model_type is PurchaseDraft:
            return cart_container_factory()
        elif model_type is StoreItem:
            store = store_factory('Moscow')
            return store_item_container_factory(name='potatoes', amount=1, store=store, price=1)
        elif model_type is Store:
            return AggregateContainer(store_factory('Moscow'), dependencies={})
        else:
            raise ValueError(f'Unknown model type {model_type}')

    return factory

