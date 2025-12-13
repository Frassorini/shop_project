from typing import Type

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class ResourcesRegistry:
    _registry: set[Type[PersistableEntity]] = set()

    @classmethod
    def register(cls, resource_type: Type[PersistableEntity]) -> None:
        if resource_type in cls._registry:
            raise ValueError(f"Resource type {resource_type} already registered")

        cls._registry.add(resource_type)

    @classmethod
    def get_map(cls) -> list[Type[PersistableEntity]]:
        return list(cls._registry)
