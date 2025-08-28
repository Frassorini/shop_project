from typing import Any, Callable, Type

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.store import Store
from shop_project.infrastructure.resource_manager.resource_snapshot import EntitySnapshot, EntitySnapshotSet, ResourceSnapshot
from shop_project.domain.customer_order import CustomerOrder
from shop_project.application.dto.mapper import to_dto


def get_resource_snapshot(resources: dict[Type[BaseAggregate], list[BaseAggregate]]) -> ResourceSnapshot:
        snapshot_set_vector: dict[Type[BaseAggregate], EntitySnapshotSet] = {}
        for resource_type in resources:
            snapshot_set_vector[resource_type] = EntitySnapshotSet([EntitySnapshot(to_dto(item)) for item in resources[resource_type]])
        
        return ResourceSnapshot(snapshot_set_vector)


def test_identity_snapshot(customer_order_factory: Callable[[], CustomerOrder],
                           store_factory_with_cache: Callable[[str], Store],):
    customer_order_1 = customer_order_factory()
    customer_order_2 = customer_order_factory()
    
    customer_order_1_snap = EntitySnapshot(to_dto(customer_order_1))
    customer_order_2_snap = EntitySnapshot(to_dto(customer_order_2))
    
    assert not customer_order_1_snap.compare_identity(customer_order_2_snap)
    assert not customer_order_1_snap.compare_content(customer_order_2_snap)
    
    assert customer_order_1_snap.compare_identity(customer_order_1_snap)
    assert customer_order_1_snap.compare_content(customer_order_1_snap)
    
    
    customer_order_1.store_id = store_factory_with_cache('New York').entity_id
    customer_order_1_snap_new = EntitySnapshot(to_dto(customer_order_1))
     
    assert customer_order_1_snap.compare_identity(customer_order_1_snap_new)
    assert not customer_order_1_snap.compare_content(customer_order_1_snap_new)
    


def test_intersect(customer_order_factory: Callable[[], CustomerOrder],
                   store_factory_with_cache: Callable[[str], Store],):
    customer_order_1 = customer_order_factory()
    customer_order_2 = customer_order_factory()
    snapshot_before: ResourceSnapshot = get_resource_snapshot({CustomerOrder: [customer_order_1, customer_order_2]})
    
    customer_order_1_old = to_dto(customer_order_1)
    customer_order_1.store_id = store_factory_with_cache('New York').entity_id
    
    snapshot_after: ResourceSnapshot = get_resource_snapshot({CustomerOrder: [customer_order_1, customer_order_2]})
    
    customer_order_2_snapshot = to_dto(customer_order_2)

    intersect_by_id_before_side = snapshot_before.intersect_identity(snapshot_after)
    assert intersect_by_id_before_side.to_dict()[CustomerOrder] == [customer_order_1_old, customer_order_2_snapshot]
    
    intersect_by_id_after_side = snapshot_after.intersect_identity(snapshot_before)
    assert intersect_by_id_after_side.to_dict()[CustomerOrder] == [to_dto(customer_order_1), customer_order_2_snapshot]
    
    intersect_by_content_before_side = snapshot_before.intersect_content(snapshot_after)
    assert intersect_by_content_before_side.to_dict()[CustomerOrder] == [customer_order_2_snapshot]
    
    intersect_by_content_after_side = snapshot_after.intersect_content(snapshot_before)
    assert intersect_by_content_after_side.to_dict()[CustomerOrder] == [customer_order_2_snapshot]


def test_difference(customer_order_factory: Callable[[], CustomerOrder],
                    store_factory_with_cache: Callable[[str], Store],):
    customer_order_1 = customer_order_factory()
    customer_order_2 = customer_order_factory()
    
    snapshot_before: ResourceSnapshot = get_resource_snapshot({CustomerOrder: [customer_order_1, customer_order_2]})
    
    customer_order_1.store_id = store_factory_with_cache('New York').entity_id
    
    snapshot_after: ResourceSnapshot = get_resource_snapshot({CustomerOrder: [customer_order_1, customer_order_2]})

    difference_by_id_before_side = snapshot_before.difference_identity(snapshot_after)
    assert not difference_by_id_before_side.to_dict()[CustomerOrder]
    
    difference_by_id_after_side = snapshot_after.difference_identity(snapshot_before)
    assert not difference_by_id_after_side.to_dict()[CustomerOrder]
     