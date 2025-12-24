from abc import ABC
from typing import Any, Literal, Sequence, Type, TypeVar, cast
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO
from shop_project.application.dto.mapper import to_dto
from shop_project.application.interfaces.interface_resource_container import (
    IResourceContainer,
)
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.exceptions import ResourcesException
from shop_project.infrastructure.persistence.resource_manager.resource_snapshot import (
    EntitySnapshot,
    EntitySnapshotSet,
    ResourceSnapshot,
)

T = TypeVar("T", bound=PersistableEntity)


class ResourceSnapshotSentinelMixin(ABC):
    resources: dict[Type[PersistableEntity], list[PersistableEntity]]
    _resource_snapshot_previous: ResourceSnapshot | None
    _resource_snapshot_current: ResourceSnapshot | None

    def _get_resource_snapshot(self) -> ResourceSnapshot:
        snapshot_set_vector: dict[Type[PersistableEntity], EntitySnapshotSet] = {}
        for resource_type in self.resources:
            snapshot_set_vector[resource_type] = EntitySnapshotSet(
                [EntitySnapshot(to_dto(item)) for item in self.resources[resource_type]]
            )

        return ResourceSnapshot(snapshot_set_vector)

    def take_snapshot(self) -> None:
        if self._resource_snapshot_previous is not None:
            raise RuntimeError("Snapshots are already taken")

        self._resource_snapshot_previous = self._resource_snapshot_current
        self._resource_snapshot_current = self._get_resource_snapshot()

    def get_resource_changes(
        self,
    ) -> dict[
        Type[PersistableEntity],
        dict[Literal["CREATED", "UPDATED", "DELETED"], list[BaseDTO[Any]]],
    ]:
        if (
            self._resource_snapshot_current is None
            or self._resource_snapshot_previous is None
        ):
            raise RuntimeError("Snapshots are not taken yet")

        deleted_snapshot: ResourceSnapshot = (
            self._resource_snapshot_previous.difference_identity(
                self._resource_snapshot_current
            )
        )
        created_snapshot: ResourceSnapshot = (
            self._resource_snapshot_current.difference_identity(
                self._resource_snapshot_previous
            )
        )
        current_snapshot_side_intersection: ResourceSnapshot = (
            self._resource_snapshot_current.intersect_identity(
                self._resource_snapshot_previous
            )
        )
        updated_snapshot: ResourceSnapshot = (
            current_snapshot_side_intersection.difference_content(
                self._resource_snapshot_previous
            )
        )

        result: dict[
            Type[PersistableEntity],
            dict[Literal["CREATED", "UPDATED", "DELETED"], list[BaseDTO[Any]]],
        ] = {}
        for item_type in self.resources.keys():
            result[item_type] = {
                "CREATED": [],
                "UPDATED": [],
                "DELETED": [],
            }

        for item_type, items in deleted_snapshot.to_dict().items():
            result[item_type]["DELETED"].extend(items)

        for item_type, items in updated_snapshot.to_dict().items():
            result[item_type]["UPDATED"].extend(items)

        for item_type, items in created_snapshot.to_dict().items():
            result[item_type]["CREATED"].extend(items)

        return result


class ResourceContainer(ResourceSnapshotSentinelMixin, IResourceContainer):
    def __init__(self, resources_registry: list[Type[PersistableEntity]]):
        self.resources: dict[Type[PersistableEntity], list[PersistableEntity]] = {
            resource: [] for resource in resources_registry
        }
        self._resource_snapshot_previous: ResourceSnapshot | None = None
        self._resource_snapshot_current: ResourceSnapshot | None = None

    def _get_resource_by_type(self, resource_type: Type[T]) -> list[T]:
        if resource_type in self.resources:
            return cast(list[T], self.resources[resource_type])
        raise NotImplementedError(f"No resource for {resource_type}")

    def get_by_attribute(
        self, model_type: Type[T], attribute_name: str, values: list[Any]
    ) -> list[T]:

        resource = self._get_resource_by_type(model_type)

        result: list[T] = []
        for item in resource:
            if getattr(item, attribute_name) in values:
                result.append(item)
        return result

    def get_one_or_none_by_attribute(
        self, model_type: Type[T], attribute_name: str, value: Any
    ) -> T | None:
        result: list[T] = self.get_by_attribute(model_type, attribute_name, [value])

        if not result:
            return None

        if len(result) > 1:
            raise RuntimeError(
                f"Found more than one {model_type} with attribute {attribute_name}=={value}"
            )

        return result[0]

    def get_one_by_attribute(
        self, model_type: Type[T], attribute_name: str, value: Any
    ) -> T:
        result: list[T] = self.get_by_attribute(model_type, attribute_name, [value])

        if not result:
            raise ResourcesException(
                f"Could not find {model_type} with attribute {attribute_name}=={value}"
            )

        if len(result) > 1:
            raise RuntimeError(
                f"Found more than one {model_type} with attribute {attribute_name}=={value}"
            )

        return result[0]

    def get_by_id(self, model_type: Type[T], entity_id: UUID) -> T:
        result: T = self.get_one_by_attribute(model_type, "entity_id", entity_id)
        return result

    def get_by_id_or_none(self, model_type: Type[T], entity_id: UUID) -> T | None:
        result: T | None = self.get_one_or_none_by_attribute(
            model_type, "entity_id", entity_id
        )
        return result

    def get_by_ids(self, model_type: Type[T], entity_ids: list[UUID]) -> list[T]:
        result: list[T] = self.get_by_attribute(model_type, "entity_id", entity_ids)

        if not result:
            raise ResourcesException(
                f"Could not find any {model_type} with ids {entity_ids}"
            )

        return result

    def get_all(self, model_type: Type[T]) -> Sequence[T]:
        return self._get_resource_by_type(model_type).copy()

    def put(self, model_type: Type[PersistableEntity], item: PersistableEntity) -> None:
        if not isinstance(item, model_type):
            raise ResourcesException(
                f"Cannot put {type(item)} into container for {model_type}"
            )

        self._get_resource_by_type(model_type).append(item)

    def put_many(
        self, model_type: Type[PersistableEntity], items: list[PersistableEntity]
    ) -> None:
        for item in items:
            self.put(model_type, item)

    def delete(
        self, model_type: Type[PersistableEntity], item: PersistableEntity
    ) -> None:
        self._get_resource_by_type(model_type).remove(item)

    def delete_many(
        self, model_type: Type[PersistableEntity], items: Sequence[PersistableEntity]
    ) -> None:
        for item in items:
            self.delete(model_type, item)
