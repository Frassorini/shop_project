from typing import Protocol, Type, TypeVar

from shop_project.application.tasks.base_task_handler import (
    BaseTaskHandler,
    BaseTaskParams,
)
from shop_project.infrastructure.entities.task import Task

T = TypeVar("T", bound=BaseTaskParams)


class ITaskFactory(Protocol):
    @classmethod
    def create(cls, use_case_type: Type[BaseTaskHandler[T]], params: T) -> Task: ...
