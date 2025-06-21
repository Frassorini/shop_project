from typing import Any, Callable, Type

import pytest
from application.resource_loader.resource_manager import ResourceContainer
from application.resource_loader.resource_snapshot import EntitySnapshot, EntitySnapshotSet, ResourceSnapshot
from domain.customer_order import CustomerOrder
from shared.entity_id import EntityId
from shared.p_snapshotable import PSnapshotable


def get_resource_snapshot(resources: dict[Type[PSnapshotable], list[Any]]) -> ResourceSnapshot:
        snapshot_set_vector: dict[Type[PSnapshotable], EntitySnapshotSet] = {}
        for resource_type in resources:
            snapshot_set_vector[resource_type] = EntitySnapshotSet([EntitySnapshot(item.snapshot()) for item in resources[resource_type]])
        
        return ResourceSnapshot(snapshot_set_vector)


def test_identity_snapshot(customer_order_factory: Callable[[], CustomerOrder]):
    customer_order_1 = customer_order_factory()
    customer_order_2 = customer_order_factory()
    
    customer_order_1_snap = EntitySnapshot(customer_order_1.snapshot())
    customer_order_2_snap = EntitySnapshot(customer_order_2.snapshot())
    
    assert not customer_order_1_snap.compare_identity(customer_order_2_snap)
    assert not customer_order_1_snap.compare_content(customer_order_2_snap)
    
    assert customer_order_1_snap.compare_identity(customer_order_1_snap)
    assert customer_order_1_snap.compare_content(customer_order_1_snap)
    
    
    customer_order_1.store = 'New York'
    customer_order_1_snap_new = EntitySnapshot(customer_order_1.snapshot())
     
    assert customer_order_1_snap.compare_identity(customer_order_1_snap_new)
    assert not customer_order_1_snap.compare_content(customer_order_1_snap_new)
    


def test_intersect(customer_order_factory: Callable[[], CustomerOrder]):
    customer_order_1 = customer_order_factory()
    customer_order_2 = customer_order_factory()
    snapshot_before: ResourceSnapshot = get_resource_snapshot({CustomerOrder: [customer_order_1, customer_order_2]})
    
    customer_order_1_old = customer_order_1.snapshot()
    customer_order_1.store = 'New York'
    
    snapshot_after: ResourceSnapshot = get_resource_snapshot({CustomerOrder: [customer_order_1, customer_order_2]})
    
    customer_order_2_snapshot = customer_order_2.snapshot()

    intersect_by_id_before_side = snapshot_before.intersect_identity(snapshot_after)
    assert intersect_by_id_before_side.to_dict()[CustomerOrder] == [customer_order_1_old, customer_order_2_snapshot]
    
    intersect_by_id_after_side = snapshot_after.intersect_identity(snapshot_before)
    assert intersect_by_id_after_side.to_dict()[CustomerOrder] == [customer_order_1.snapshot(), customer_order_2_snapshot]
    
    intersect_by_content_before_side = snapshot_before.intersect_content(snapshot_after)
    assert intersect_by_content_before_side.to_dict()[CustomerOrder] == [customer_order_2_snapshot]
    
    intersect_by_content_after_side = snapshot_after.intersect_content(snapshot_before)
    assert intersect_by_content_after_side.to_dict()[CustomerOrder] == [customer_order_2_snapshot]


def test_difference(customer_order_factory: Callable[[], CustomerOrder]):
    customer_order_1 = customer_order_factory()
    customer_order_2 = customer_order_factory()
    
    snapshot_before: ResourceSnapshot = get_resource_snapshot({CustomerOrder: [customer_order_1, customer_order_2]})
    
    customer_order_1.store = 'New York'
    
    snapshot_after: ResourceSnapshot = get_resource_snapshot({CustomerOrder: [customer_order_1, customer_order_2]})

    difference_by_id_before_side = snapshot_before.difference_identity(snapshot_after)
    assert not difference_by_id_before_side.to_dict()[CustomerOrder]
    
    difference_by_id_after_side = snapshot_after.difference_identity(snapshot_before)
    assert not difference_by_id_after_side.to_dict()[CustomerOrder]
     