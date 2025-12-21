import traceback
import warnings
from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING, Any, Awaitable, Callable

import pytest
from dishka import AsyncContainer
from taskiq import TaskiqMessage, TaskiqMiddleware, TaskiqResult

from shop_project.infrastructure.background_tasks.application_task_sender_service import (
    TaskSender,
)
from shop_project.infrastructure.entities.task import Task
from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWorkFactory

if TYPE_CHECKING:
    from taskiq import AsyncBroker

from shop_project.infrastructure.background_tasks.broker import (
    make_broker,
    make_broker_inmem,
    producer_broker_context_factory,
)


class LogErrorsMiddleware(TaskiqMiddleware):
    async def on_error(
        self,
        message: TaskiqMessage,
        result: TaskiqResult[Any],
        exception: BaseException,
    ) -> None:
        tb_str = "".join(
            traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )
        )
        warnings.warn(category=RuntimeWarning, message=tb_str)
        # pytest.fail("background task failed", pytrace=False)


@pytest.fixture
def setup_broker(
    request: pytest.FixtureRequest,
) -> Callable[["AsyncBroker", AsyncContainer], None]:
    def _inner(broker: "AsyncBroker", async_container: AsyncContainer) -> None:
        broker.state["di_container"] = async_container
        if not request.config.getoption("--real-broker"):
            broker.add_middlewares(LogErrorsMiddleware())

    return _inner


@pytest.fixture
def test_broker_container_factory(
    request: pytest.FixtureRequest,
) -> Callable[[], AbstractAsyncContextManager["AsyncBroker"]]:
    if request.config.getoption("--real-broker"):
        return producer_broker_context_factory(make_broker)
    else:
        return producer_broker_context_factory(make_broker_inmem)


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
