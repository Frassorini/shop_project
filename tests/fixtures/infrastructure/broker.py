from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator, Callable

import pytest
import pytest_asyncio
from dishka import AsyncContainer

from shop_project.infrastructure.message_broker.broker import (
    make_broker,
    make_broker_inmem,
    producer_broker_context_factory,
)
from shop_project.infrastructure.message_broker.broker_container import BrokerContainer


@pytest_asyncio.fixture
async def test_broker_container(
    async_container: AsyncContainer,
) -> AsyncGenerator[BrokerContainer, None]:
    yield await async_container.get(BrokerContainer)


@pytest.fixture
def test_broker_container_factory(
    request: pytest.FixtureRequest,
) -> Callable[[], AbstractAsyncContextManager[BrokerContainer]]:
    if request.config.getoption("--real-broker"):
        return producer_broker_context_factory(make_broker)
    else:
        return producer_broker_context_factory(make_broker_inmem)
