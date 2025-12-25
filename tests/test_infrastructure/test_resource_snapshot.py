from typing import Callable, Type

from shop_project.application.shared.dto.mapper import to_dto
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.persistence.resource_manager.resource_snapshot import (
    EntitySnapshot,
    EntitySnapshotSet,
    ResourceSnapshot,
)


def get_resource_snapshot(
    resources: dict[Type[PersistableEntity], list[PersistableEntity]],
) -> ResourceSnapshot:
    snapshot_set_vector: dict[Type[PersistableEntity], EntitySnapshotSet] = {}
    for resource_type in resources:
        snapshot_set_vector[resource_type] = EntitySnapshotSet(
            [EntitySnapshot(to_dto(item)) for item in resources[resource_type]]
        )

    return ResourceSnapshot(snapshot_set_vector)


def test_identity_snapshot(purchase_draft_factory: Callable[[], PurchaseDraft]):
    purchase_draft_1 = purchase_draft_factory()
    purchase_draft_2 = purchase_draft_factory()

    purchase_draft_1_snap = EntitySnapshot(to_dto(purchase_draft_1))
    purchase_draft_2_snap = EntitySnapshot(to_dto(purchase_draft_2))

    assert not purchase_draft_1_snap.compare_identity(purchase_draft_2_snap)
    assert not purchase_draft_1_snap.compare_content(purchase_draft_2_snap)

    assert purchase_draft_1_snap.compare_identity(purchase_draft_1_snap)
    assert purchase_draft_1_snap.compare_content(purchase_draft_1_snap)

    purchase_draft_1.finalize()
    purchase_draft_1_snap_new = EntitySnapshot(to_dto(purchase_draft_1))

    assert purchase_draft_1_snap.compare_identity(purchase_draft_1_snap_new)
    assert not purchase_draft_1_snap.compare_content(purchase_draft_1_snap_new)


def test_intersect(purchase_draft_factory: Callable[[], PurchaseDraft]):
    purchase_draft_1 = purchase_draft_factory()
    purchase_draft_2 = purchase_draft_factory()
    snapshot_before: ResourceSnapshot = get_resource_snapshot(
        {PurchaseDraft: [purchase_draft_1, purchase_draft_2]}
    )

    purchase_draft_1_snapshot = to_dto(purchase_draft_1)

    purchase_draft_1.finalize()

    snapshot_after: ResourceSnapshot = get_resource_snapshot(
        {PurchaseDraft: [purchase_draft_1, purchase_draft_2]}
    )

    purchase_draft_2_snapshot = to_dto(purchase_draft_2)

    intersect_by_id_before_side = snapshot_before.intersect_identity(snapshot_after)
    assert intersect_by_id_before_side.to_dict()[PurchaseDraft] == [
        purchase_draft_1_snapshot,
        purchase_draft_2_snapshot,
    ]

    intersect_by_id_after_side = snapshot_after.intersect_identity(snapshot_before)
    assert intersect_by_id_after_side.to_dict()[PurchaseDraft] == [
        to_dto(purchase_draft_1),
        purchase_draft_2_snapshot,
    ]

    intersect_by_content_before_side = snapshot_before.intersect_content(snapshot_after)
    assert intersect_by_content_before_side.to_dict()[PurchaseDraft] == [
        purchase_draft_2_snapshot
    ]

    intersect_by_content_after_side = snapshot_after.intersect_content(snapshot_before)
    assert intersect_by_content_after_side.to_dict()[PurchaseDraft] == [
        purchase_draft_2_snapshot
    ]


def test_difference(purchase_draft_factory: Callable[[], PurchaseDraft]):
    purchase_draft_1 = purchase_draft_factory()
    purchase_draft_2 = purchase_draft_factory()

    snapshot_before: ResourceSnapshot = get_resource_snapshot(
        {PurchaseDraft: [purchase_draft_1, purchase_draft_2]}
    )

    purchase_draft_1_snapshot = to_dto(purchase_draft_1)
    purchase_draft_1.finalize()

    snapshot_after: ResourceSnapshot = get_resource_snapshot(
        {PurchaseDraft: [purchase_draft_1, purchase_draft_2]}
    )

    difference_by_id_before_side = snapshot_before.difference_identity(snapshot_after)
    assert not difference_by_id_before_side.to_dict()[PurchaseDraft]

    difference_by_id_after_side = snapshot_after.difference_identity(snapshot_before)
    assert not difference_by_id_after_side.to_dict()[PurchaseDraft]

    difference_by_content_before_side = snapshot_before.difference_content(
        snapshot_after
    )
    assert difference_by_content_before_side.to_dict()[PurchaseDraft] == [
        purchase_draft_1_snapshot
    ]

    difference_by_content_after_side = snapshot_after.difference_content(
        snapshot_before
    )
    assert difference_by_content_after_side.to_dict()[PurchaseDraft] == [
        to_dto(purchase_draft_1)
    ]
