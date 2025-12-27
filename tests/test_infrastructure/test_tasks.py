from typing import AsyncContextManager, Awaitable, Callable, Type

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.background.implementations.example_task_handler import (
    ExampleTaskHandler,
    ExampleTaskParams,
)
from shop_project.application.entities.task import Task, create_task
from shop_project.application.shared.interfaces.interface_task_sender import ITaskSender
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.persistence.query.query_builder import QueryBuilder
from shop_project.infrastructure.persistence.unit_of_work import (
    UnitOfWork,
    UnitOfWorkFactory,
)


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

    task = create_task(ExampleTaskHandler, ExampleTaskParams(message="test"))

    async with uow_factory.create(QueryBuilder(mutating=True).build()) as uow:
        uow.get_resources().put(Task, task)
        uow.mark_commit()

    await ensure_tasks_completion()

    async with uow_check(Task, task) as uow:
        resources = uow.get_resources()
        tasks = resources.get_all(Task)

    assert len(tasks) == 0
