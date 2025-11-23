from typing import Self
from uuid import UUID

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class Manager(PersistableEntity):
    entity_id: UUID
    name: str

    def __init__(self, entity_id: UUID, name: str) -> None:
        self.entity_id: UUID = entity_id
        self.name: str = name

    @classmethod
    def _load(cls, entity_id: UUID, name: str) -> Self:
        obj = cls.__new__(cls)

        obj.entity_id = entity_id
        obj.name = name

        return obj
