from dataclasses import dataclass, field
from typing import Generic, Type, TypeVar
from shop_project.domain.persistable_entity import PersistableEntity


T = TypeVar("T", bound="PersistableEntity")


class AggregateDependencies:
    def __init__(self, items: dict[Type[PersistableEntity], list[PersistableEntity]]) -> None:
        self.dependencies: dict[Type[PersistableEntity], list[PersistableEntity]] = items

    def __getitem__(self, agg_type: Type[T]) -> list[T]:
        if not issubclass(agg_type, PersistableEntity):
            raise TypeError(f"Expected subclass of PersistableEntity, got {agg_type!r}")

        if agg_type not in self.dependencies:
            raise KeyError(f"No dependencies found for {agg_type.__name__}")

        deps = self.dependencies[agg_type]
        if not all(isinstance(dep, agg_type) for dep in deps):
            raise TypeError(
                f"Dependencies for {agg_type.__name__} contain objects of incorrect type"
            )

        return deps # type: ignore[return-value]


class AggregateContainer:
    def __init__(self, aggregate: PersistableEntity, dependencies: dict[Type[PersistableEntity], list[PersistableEntity]]) -> None:
        self.aggregate = aggregate
        self.dependencies = AggregateDependencies(dependencies)