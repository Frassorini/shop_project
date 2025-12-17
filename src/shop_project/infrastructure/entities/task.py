from typing import Self
from uuid import UUID

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class Task(PersistableEntity):
    def __init__(self, entity_id: UUID, handler: str, params_json: str) -> None:
        self.entity_id: UUID = entity_id
        self.handler: str = handler
        self.params_json: str = params_json

    @classmethod
    def load(cls, entity_id: UUID, handler: str, params_json: str) -> Self:
        obj = cls.__new__(cls)

        obj.entity_id = entity_id
        obj.handler = handler
        obj.params_json = params_json

        return obj
