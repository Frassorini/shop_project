from typing import AsyncContextManager, Awaitable, Callable, Type

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.interfaces.interface_task_factory import ITaskFactory
from shop_project.application.interfaces.interface_task_sender import ITaskSender
from shop_project.application.tasks.implementations.example_task_handler import (
    ExampleTaskHandler,
    ExampleTaskParams,
)
from shop_project.infrastructure.entities.task import Task
from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWork, UnitOfWorkFactory
from tests.test_infrastructure.test_unit_of_work import PersistableEntity


@pytest.mark.asyncio
async def test_background_tasks(
    async_container: AsyncContainer,
    uow_factory: UnitOfWorkFactory,
    ensure_tasks_completion: Callable[[], Awaitable[None]],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
) -> None:
    application_task_sender = await async_container.get(ITaskSender)
    task_factory = await async_container.get(ITaskFactory)

    task = task_factory.create(ExampleTaskHandler, ExampleTaskParams(message="test"))

    async with uow_factory.create(QueryBuilder(mutating=True).build()) as uow:
        uow.get_resorces().put(Task, task)
        uow.mark_commit()

    await ensure_tasks_completion()

    async with uow_check(Task, task) as uow:
        resources = uow.get_resorces()
        tasks = resources.get_all(Task)

    assert len(tasks) == 0
