from typing import Type, TypeVar
from uuid import uuid4

from shop_project.application.background.base_task_handler import (
    BaseTaskHandler,
    BaseTaskParams,
)
from shop_project.application.shared.interfaces.interface_task_factory import (
    ITaskFactory,
)
from shop_project.infrastructure.entities.task import Task

T = TypeVar("T", bound=BaseTaskParams)


class TaskFactory(ITaskFactory):
    @classmethod
    def create(cls, use_case_type: Type[BaseTaskHandler[T]], params: T) -> Task:
        params_json = params.model_dump_json()
        return Task(
            entity_id=uuid4(),
            handler=use_case_type.handler_name,
            params_json=params_json,
        )
