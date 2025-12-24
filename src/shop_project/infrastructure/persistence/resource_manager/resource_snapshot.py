from typing import Any, Self, Type
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO
from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class EntitySnapshot:
    def __init__(self, snapshot: BaseDTO[Any]) -> None:
        if not hasattr(snapshot, "entity_id"):
            raise ValueError("Snapshot must have entity_id attribute")

        self.entity_id: UUID = snapshot.entity_id
        self.snapshot: BaseDTO[Any] = snapshot

    def compare_identity(self, other: Self) -> bool:
        return self.entity_id == other.entity_id

    def compare_content(self, other: Self) -> bool:
        return self.snapshot == other.snapshot


class EntitySnapshotSet:
    def __init__(self, snapshots: list[EntitySnapshot]) -> None:
        self.snapshots: list[EntitySnapshot] = snapshots

    def in_by_identity(self, other_snapshot: EntitySnapshot) -> bool:
        for snapshot in self.snapshots:
            if snapshot.compare_identity(other_snapshot):
                return True

        return False

    def in_by_content(self, other_snapshot: EntitySnapshot) -> bool:
        for snapshot in self.snapshots:
            if snapshot.compare_content(other_snapshot):
                return True

        return False

    def intersection_identity(self, other: Self) -> Self:
        result: list[EntitySnapshot] = []

        for snapshot in self.snapshots:
            for other_snapshot in other.snapshots:
                if snapshot.compare_identity(other_snapshot):
                    result.append(snapshot)

        return self.__class__(result)

    def intersection_content(self, other: Self) -> Self:
        result: list[EntitySnapshot] = []

        for snapshot in self.snapshots:
            for other_snapshot in other.snapshots:
                if snapshot.compare_content(other_snapshot):
                    result.append(snapshot)

        return self.__class__(result)

    def difference_identity(self, other: Self) -> Self:
        result: list[EntitySnapshot] = []

        for snapshot in self.snapshots:
            if not other.in_by_identity(snapshot):
                result.append(snapshot)

        return self.__class__(result)

    def difference_content(self, other: Self) -> Self:
        result: list[EntitySnapshot] = []

        for snapshot in self.snapshots:
            if not other.in_by_content(snapshot):
                result.append(snapshot)

        return self.__class__(result)


class ResourceSnapshot:
    def __init__(
        self, snapshotset_vector: dict[Type[PersistableEntity], EntitySnapshotSet]
    ) -> None:
        self.snapshot_set_vector: dict[Type[PersistableEntity], EntitySnapshotSet] = (
            snapshotset_vector
        )

    def intersect_identity(self, other: Self) -> Self:
        result: dict[Type[PersistableEntity], EntitySnapshotSet] = {}

        for resource_type in self.snapshot_set_vector:
            result[resource_type] = self.snapshot_set_vector[
                resource_type
            ].intersection_identity(other.snapshot_set_vector[resource_type])

        return self.__class__(result)

    def intersect_content(self, other: Self) -> Self:
        result: dict[Type[PersistableEntity], EntitySnapshotSet] = {}

        for resource_type in self.snapshot_set_vector:
            result[resource_type] = self.snapshot_set_vector[
                resource_type
            ].intersection_content(other.snapshot_set_vector[resource_type])

        return self.__class__(result)

    def difference_identity(self, other: Self) -> Self:
        result: dict[Type[PersistableEntity], EntitySnapshotSet] = {}

        for resource_type in self.snapshot_set_vector:
            result[resource_type] = self.snapshot_set_vector[
                resource_type
            ].difference_identity(other.snapshot_set_vector[resource_type])

        return self.__class__(result)

    def difference_content(self, other: Self) -> Self:
        result: dict[Type[PersistableEntity], EntitySnapshotSet] = {}

        for resource_type in self.snapshot_set_vector:
            result[resource_type] = self.snapshot_set_vector[
                resource_type
            ].difference_content(other.snapshot_set_vector[resource_type])

        return self.__class__(result)

    def to_dict(self) -> dict[Type[PersistableEntity], list[BaseDTO[Any]]]:
        result: dict[Type[PersistableEntity], list[BaseDTO[Any]]] = {}

        for resource_type in self.snapshot_set_vector:
            result[resource_type] = [
                snapshot.snapshot
                for snapshot in self.snapshot_set_vector[resource_type].snapshots
            ]

        return result
