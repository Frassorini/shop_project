from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator, Callable
import pytest
import pytest_asyncio
from shop_project.infrastructure.dependency_injection.domain.container import DomainContainer
from tests.fixtures.infrastructure.database import Database

@pytest.fixture
def domain_container() -> DomainContainer:
    container = DomainContainer()

    return container
