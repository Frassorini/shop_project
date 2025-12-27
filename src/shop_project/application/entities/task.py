from typing import Self, Type, TypeVar
from uuid import UUID, uuid4

from shop_project.application.background.base_task_handler import (
    BaseTaskHandler,
    BaseTaskParams,
)
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


T = TypeVar("T", bound=BaseTaskParams)


def create_task(use_case_type: Type[BaseTaskHandler[T]], params: T) -> Task:
    params_json = params.model_dump_json()
    return Task(
        entity_id=uuid4(),
        handler=use_case_type.handler_name,
        params_json=params_json,
    )
