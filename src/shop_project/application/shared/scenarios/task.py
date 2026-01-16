from typing import Type, TypeVar
from uuid import UUID

from shop_project.application.background.base_task_handler import (
    BaseTaskHandler,
    BaseTaskParams,
)
from shop_project.application.background.exceptions import AlreadyDoneException
from shop_project.application.entities.task import Task, create_task
from shop_project.application.shared.interfaces.interface_resource_container import (
    IResourceContainer,
)


def capture_task(resources: IResourceContainer, task_id: UUID) -> BaseTaskParams | None:
    task = resources.get_by_id_or_none(Task, task_id)

    if not task:
        raise AlreadyDoneException("Task is already done")

    resources.delete(Task, task)

    return BaseTaskParams.model_validate_json(task.params_json)


T = TypeVar("T", bound=BaseTaskParams)


def enqueue_task(
    resources: IResourceContainer, use_case_type: Type[BaseTaskHandler[T]], params: T
) -> UUID:
    task = create_task(use_case_type, params)
    resources.put(Task, task)
    return task.entity_id
