import traceback
import warnings
from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING, Any, Callable

import pytest
from dishka import AsyncContainer
from taskiq import TaskiqMessage, TaskiqMiddleware, TaskiqResult

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
