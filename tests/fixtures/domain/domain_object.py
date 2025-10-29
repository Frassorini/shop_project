from os import name
from typing import Any, Callable, Type, TypeVar, cast
from uuid import uuid4
from plum import overload, dispatch

import pytest

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
                          purchase_active_filled_container_factory: Callable[[], AggregateContainer],
                          supplier_order_container_factory: Callable[[], AggregateContainer],
                          purchase_draft_container_factory: Callable[[], AggregateContainer],
                          store_item_container_factory: Callable[..., AggregateContainer]
                          ) -> Callable[[Type[BaseAggregate]], AggregateContainer]:
    def factory(model_type: Type[BaseAggregate]) -> AggregateContainer:
        if model_type is Customer:
            return AggregateContainer(customer_andrew(), dependencies={})
        elif model_type is PurchaseActive:
            return purchase_active_filled_container_factory()
        elif model_type is SupplierOrder:
            return supplier_order_container_factory()
        elif model_type is PurchaseDraft:
            return purchase_draft_container_factory()
        elif model_type is StoreItem:
            return store_item_container_factory(name='potatoes', amount=1, price=1)
        else:
            raise ValueError(f'Unknown model type {model_type}')

    return factory

