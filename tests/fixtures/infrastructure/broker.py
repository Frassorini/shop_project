from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING, Callable

import pytest
from dishka import AsyncContainer

if TYPE_CHECKING:
    from taskiq import AsyncBroker

from shop_project.infrastructure.background_tasks.broker import (
    make_broker,
    make_broker_inmem,
    producer_broker_context_factory,
)


@pytest.fixture
def setup_broker() -> Callable[["AsyncBroker", AsyncContainer], None]:
    def _inner(broker: "AsyncBroker", async_container: AsyncContainer) -> None:
        broker.state["di_container"] = async_container

    return _inner


@pytest.fixture
def test_broker_container_factory(
    request: pytest.FixtureRequest,
) -> Callable[[], AbstractAsyncContextManager["AsyncBroker"]]:
    if request.config.getoption("--real-broker"):
        return producer_broker_context_factory(make_broker)
    else:
        return producer_broker_context_factory(make_broker_inmem)
