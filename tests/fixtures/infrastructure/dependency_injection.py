from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator, Callable, Generator
from dependency_injector import providers
from dishka import make_async_container, make_container
from dishka.container import Container
import pytest
import pytest_asyncio
from shop_project.infrastructure.dependency_injection.domain.container import DomainProvider
from tests.fixtures.infrastructure.database import Database

@pytest.fixture
def di_container() -> Container:
    container = make_container(DomainProvider())

    return container
