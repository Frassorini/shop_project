from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator, Callable, Generator
from dishka import make_async_container, make_container
from dishka.container import Container
from dishka.async_container import AsyncContainer
import pytest
import pytest_asyncio
from shop_project.infrastructure.dependency_injection.domain.container import DomainProvider
from shop_project.infrastructure.dependency_injection.infrastructure.container import InfrastructureProvider
from tests.fixtures.infrastructure.database import Database

@pytest.fixture()
def domain_container() -> Container:
    container = make_container(DomainProvider())

    return container


@pytest_asyncio.fixture()
async def async_container(test_db_factory: Callable[[], AbstractAsyncContextManager[Database]]) -> AsyncGenerator[AsyncContainer, None]:
    container = make_async_container(DomainProvider(), InfrastructureProvider(test_db_factory))
    
    async with container() as ct:
        yield ct