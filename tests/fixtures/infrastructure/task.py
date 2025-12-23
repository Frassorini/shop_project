from typing import Awaitable, Callable
from uuid import uuid4

import pytest
from dishka import AsyncContainer
from dishka.container import Container

from shop_project.infrastructure.authentication.services.session_service import (
    SessionService,
)
from shop_project.infrastructure.background_tasks.application_task_sender_service import (
    TaskSender,
)
from shop_project.infrastructure.entities.task import Task
from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWorkFactory
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
def ensure_tasks_completion(
    request: pytest.FixtureRequest,
    async_container: AsyncContainer,
    uow_factory: UnitOfWorkFactory,
) -> Callable[[], Awaitable[None]]:
    async def _inner(max_tries: int = 10) -> None:
        if request.config.getoption("--real-broker"):
            return

        task_sender = await async_container.get(TaskSender)

        for i in range(max_tries):
            async with uow_factory.create(
                QueryBuilder(mutating=False).load(Task).no_lock().build()
            ) as uow:
                resources = uow.get_resorces()

                tasks = resources.get_all(Task)

            if len(tasks) == 0:
                return

            for task in tasks:
                await task_sender.send(task)
        raise RuntimeError("Attempts to complete tasks exceeded max_tries")

    return _inner
