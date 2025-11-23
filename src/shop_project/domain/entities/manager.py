from typing import Any, Self
from uuid import UUID

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class Manager(PersistableEntity):
    def __init__(self, entity_id: UUID, name: str) -> None:
        self.entity_id: UUID = entity_id
        self.name: str = name

    def to_dict(self) -> dict[str, Any]:
        return {"entity_id": self.entity_id, "name": self.name}

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        return cls(snapshot["entity_id"], snapshot["name"])
