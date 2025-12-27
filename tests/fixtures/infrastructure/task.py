import asyncio
from typing import Awaitable, Callable, Coroutine
from uuid import uuid4

import pytest
from dishka import AsyncContainer
from dishka.container import Container

from shop_project.application.entities.task import Task
from shop_project.application.shared.interfaces.interface_task_sender import ITaskSender
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.authentication.services.session_service import (
    SessionService,
)
from shop_project.infrastructure.background_tasks.task_sender_service import (
    TaskSender,
)
from shop_project.infrastructure.persistence.query.query_builder import QueryBuilder
from shop_project.infrastructure.persistence.unit_of_work import UnitOfWorkFactory
from tests.helpers import AggregateContainer


@pytest.fixture
def task_container_factory(
    domain_container: Container,
) -> Callable[..., AggregateContainer]:

    def fact() -> AggregateContainer:
        session_service = domain_container.get(SessionService)

        application_task = Task(
            entity_id=uuid4(),
            handler="test_handler",
            params_json="{}",
        )

        return AggregateContainer(aggregate=application_task, dependencies={})

    return fact


@pytest.fixture
def inmem_save_and_send_task(
    save_entity: Callable[[PersistableEntity], Coroutine[None, None, None]],
    async_container: AsyncContainer,
) -> Callable[[Task], Awaitable[None]]:
    async def _inner(task: Task) -> None:
        task_sender = await async_container.get(ITaskSender)
        await save_entity(task)
        await task_sender.send(task)

    return _inner


@pytest.fixture
def ensure_tasks_completion(
    request: pytest.FixtureRequest,
    async_container: AsyncContainer,
    uow_factory: UnitOfWorkFactory,
) -> Callable[[], Awaitable[None]]:
    async def _inner(max_tries: int = 10) -> None:
        task_sender = await async_container.get(TaskSender)

        for i in range(max_tries):
            async with uow_factory.create(
                QueryBuilder(mutating=False).load(Task).no_lock().build()
            ) as uow:
                resources = uow.get_resources()

                tasks = resources.get_all(Task)

            if len(tasks) == 0:
                return

            for task in tasks:
                await task_sender.send(task)

            if request.config.getoption("--real-broker"):
                await asyncio.sleep(1)
        raise RuntimeError("Attempts to complete tasks exceeded max_tries")

    return _inner
