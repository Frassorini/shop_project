from typing import Callable

import pytest
from infrastructure.resource_manager.resource_manager import ResourceContainer
from domain.customer_order import CustomerOrder
from shared.entity_id import EntityId


def test_get_by_id(customer_order_factory: Callable[[], CustomerOrder]) -> None:
    container = ResourceContainer()
    customer_order_1 = customer_order_factory()
    
    container.put(CustomerOrder, customer_order_1)
    
    assert container.get_by_id(CustomerOrder, customer_order_1.entity_id) == customer_order_1


def test_get_by_attribute(customer_order_factory: Callable[[], CustomerOrder]) -> None:
    container = ResourceContainer()
    customer_order_1 = customer_order_factory()
    customer_order_2 = customer_order_factory()
    
    container.put(CustomerOrder, customer_order_1)
    container.put(CustomerOrder, customer_order_2)

    assert container.get_by_attribute(CustomerOrder, "entity_id", [customer_order_1.entity_id, customer_order_2.entity_id]) == [customer_order_1, customer_order_2]
    assert container.get_by_attribute(CustomerOrder, "customer_id", [customer_order_1.customer_id]) == [customer_order_1]
    

def test_get_by_wrong_attribute(customer_order_factory: Callable[[], CustomerOrder]) -> None:
    container = ResourceContainer()
    customer_order_1 = customer_order_factory()
    
    container.put(CustomerOrder, customer_order_1)

    with pytest.raises(AttributeError):
        container.get_by_attribute(CustomerOrder, "wrong_attribute", [customer_order_1.entity_id])


def test_get_by_id_not_found(customer_order_factory: Callable[[], CustomerOrder]) -> None:
    container = ResourceContainer()
    customer_order_1 = customer_order_factory()
    
    container.put(CustomerOrder, customer_order_1)

    with pytest.raises(ValueError):
        container.get_by_id(CustomerOrder, EntityId('99999'))


def test_snapshot_create(customer_order_factory: Callable[[], CustomerOrder]) -> None:
    container = ResourceContainer()
    container.take_snapshot()
    customer_order = customer_order_factory()
    
    container.put(CustomerOrder, customer_order)

    container.take_snapshot()
    
    assert customer_order.snapshot() in container.get_resource_changes()[CustomerOrder]['CREATED']


def test_snapshot_delete(customer_order_factory: Callable[[], CustomerOrder]) -> None:
    container = ResourceContainer()
    customer_order = customer_order_factory()
    
    container.put(CustomerOrder, customer_order)
    container.take_snapshot()
    container.delete(CustomerOrder, customer_order)
    container.take_snapshot()

    
    assert customer_order.snapshot() in container.get_resource_changes()[CustomerOrder]['DELETED']


def test_snapshot_update(customer_order_factory: Callable[[], CustomerOrder]) -> None:
    container = ResourceContainer()
    customer_order: CustomerOrder = customer_order_factory()
    
    container.put(CustomerOrder, customer_order)
    container.take_snapshot()
    customer_order.store = 'New York'
    container.take_snapshot()
    
    assert customer_order.snapshot() in container.get_resource_changes()[CustomerOrder]['UPDATED']


def test_snapshot_no_previous(customer_order_factory: Callable[[], CustomerOrder]) -> None:
    container = ResourceContainer()
    customer_order_1 = customer_order_factory()
    
    container.put(CustomerOrder, customer_order_1)

    container.take_snapshot()
    
    with pytest.raises(RuntimeError):
        container.get_resource_changes()


def test_too_many_snapshots() -> None:
    container = ResourceContainer()
    container.take_snapshot()

    container.take_snapshot()
    
    with pytest.raises(RuntimeError):
        container.take_snapshot()