from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator, Callable, Generator
from dishka import make_async_container, make_container
from dishka.container import Container
from dishka.async_container import AsyncContainer
import pytest
import pytest_asyncio

from shop_project.infrastructure.dependency_injection.domain.domain_container import DomainProvider
from shop_project.infrastructure.dependency_injection.infrastructure.database_container import DatabaseProvider
from shop_project.infrastructure.dependency_injection.infrastructure.broker_provider import BrokerProvider
from shop_project.infrastructure.dependency_injection.application.application_service_provider import ApplicationServiceProvider

from shop_project.infrastructure.message_broker.broker_container import BrokerContainer
from tests.fixtures.infrastructure.database import Database

@pytest.fixture()
def domain_container() -> Container:
    container = make_container(DomainProvider())

    return container


@pytest_asyncio.fixture()
async def async_container(test_db_factory: Callable[[], AbstractAsyncContextManager[Database]],
                          test_broker_container_factory: Callable[[], AbstractAsyncContextManager[BrokerContainer]]) -> AsyncGenerator[AsyncContainer, None]:
    container = make_async_container(
        DomainProvider(), 
        DatabaseProvider(test_db_factory),
        BrokerProvider(test_broker_container_factory),
        ApplicationServiceProvider(),
    )
    
    async with container() as ct:
        yield ct
    
    await container.close()