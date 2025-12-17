import asyncio
from typing import AsyncContextManager, Callable, Type

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.tasks.implementations.example_task_handler import (
    ExampleTaskHandler,
    ExampleTaskParams,
)
from shop_project.infrastructure.background_tasks.application_task_factory import (
    TaskFactory,
)
from shop_project.infrastructure.background_tasks.application_task_sender_service import (
    TaskSender,
)
from shop_project.infrastructure.entities.task import Task
from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWork, UnitOfWorkFactory
from tests.test_infrastructure.test_unit_of_work import PersistableEntity


@pytest.mark.asyncio
async def test_background_tasks_inmemory(
    request: pytest.FixtureRequest,
    async_container: AsyncContainer,
    uow_factory: UnitOfWorkFactory,
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
) -> None:
    wait = False

    if request.config.getoption("--real-broker"):
        wait = True

    application_task_sender = await async_container.get(TaskSender)

    task = TaskFactory.create(ExampleTaskHandler, ExampleTaskParams(message="test"))

    async with uow_factory.create(QueryBuilder(mutating=True).build()) as uow:
        uow.get_resorces().put(Task, task)
        uow.mark_commit()

    await application_task_sender.send(task)

    if wait:
        await asyncio.sleep(1)

    async with uow_check(Task, task) as uow:
        resources = uow.get_resorces()
        tasks = resources.get_all(Task)

    assert len(tasks) == 0
