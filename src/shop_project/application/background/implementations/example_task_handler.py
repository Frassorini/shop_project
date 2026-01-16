from typing import Type
from uuid import UUID

from shop_project.application.background.base_task_handler import (
    BaseTaskHandler,
    BaseTaskParams,
)
from shop_project.application.background.exceptions import RetryException
from shop_project.application.entities.task import Task
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)


class ExampleTaskParams(BaseTaskParams):
    message: str


class ExampleTaskHandler(BaseTaskHandler[ExampleTaskParams]):
    handler_name = "example"

    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._query_builder_type = query_builder_type

    async def handle(self, task_id: UUID) -> None:

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Task)
            .from_attribute("entity_id", [task_id])
            .for_update(no_wait=True)
            .build(),
            exception_on_nowait=RetryException,
        ) as uow:
            resources = uow.get_resources()

            task = resources.get_by_id_or_none(Task, task_id)
            if task is None:
                return

            params = ExampleTaskParams.model_validate_json(task.params_json)

            print(task.handler, params.message)

            resources.delete(Task, task)

            uow.mark_commit()
