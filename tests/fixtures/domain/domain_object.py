from os import name
from typing import Any, Callable, Type, TypeVar, cast
from uuid import uuid4
from plum import overload, dispatch

import pytest

from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.shipment import Shipment
from shop_project.shared.entity_id import EntityId
from shop_project.domain.interfaces.persistable_entity import PersistableEntity

from tests.helpers import AggregateContainer


@pytest.fixture
def domain_object_factory(customer_andrew: Callable[[], Customer],
                          purchase_active_filled_container_factory: Callable[[], AggregateContainer],
                          shipment_conatiner_factory: Callable[[], AggregateContainer],
                          purchase_draft_container_factory: Callable[[], AggregateContainer],
                          product_container_factory: Callable[..., AggregateContainer]
                          ) -> Callable[[Type[PersistableEntity]], AggregateContainer]:
    def factory(model_type: Type[PersistableEntity]) -> AggregateContainer:
        if model_type is Customer:
            return AggregateContainer(customer_andrew(), dependencies={})
        elif model_type is PurchaseActive:
            return purchase_active_filled_container_factory()
        elif model_type is Shipment:
            return shipment_conatiner_factory()
        elif model_type is PurchaseDraft:
            return purchase_draft_container_factory()
        elif model_type is Product:
            return product_container_factory(name='potatoes', amount=1, price=1)
        else:
            raise ValueError(f'Unknown model type {model_type}')

    return factory

