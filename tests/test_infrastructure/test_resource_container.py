from typing import Callable

import pytest
from shop_project.domain.store import Store
from shop_project.exceptions import ResourcesException
from shop_project.infrastructure.resource_manager.resource_manager import ResourceContainer
from shop_project.domain.customer_order import CustomerOrder
from shop_project.shared.entity_id import EntityId
from shop_project.application.dto.mapper import to_dto


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

    with pytest.raises(ResourcesException):
        container.get_by_id(CustomerOrder, EntityId('99999'))


def test_snapshot_create(customer_order_factory: Callable[[], CustomerOrder]) -> None:
    container = ResourceContainer()
    container.take_snapshot()
    customer_order = customer_order_factory()
    
    container.put(CustomerOrder, customer_order)

    container.take_snapshot()
    
    assert to_dto(customer_order) in container.get_resource_changes()[CustomerOrder]['CREATED']


def test_snapshot_delete(customer_order_factory: Callable[[], CustomerOrder]) -> None:
    container = ResourceContainer()
    customer_order = customer_order_factory()
    
    container.put(CustomerOrder, customer_order)
    container.take_snapshot()
    container.delete(CustomerOrder, customer_order)
    container.take_snapshot()

    
    assert to_dto(customer_order) in container.get_resource_changes()[CustomerOrder]['DELETED']


def test_snapshot_update(customer_order_factory: Callable[[], CustomerOrder],
                         store_factory_with_cache: Callable[[str], Store],) -> None:
    container = ResourceContainer()
    customer_order: CustomerOrder = customer_order_factory()
    
    container.put(CustomerOrder, customer_order)
    container.take_snapshot()
    customer_order.store_id = store_factory_with_cache('New York').entity_id
    container.take_snapshot()
    
    assert to_dto(customer_order) in container.get_resource_changes()[CustomerOrder]['UPDATED']


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