from dependency_injector.providers import Resource
from unittest.mock import MagicMock, patch

from dependency_injector import containers, providers
from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncGenerator, Awaitable, Generator

import pytest
import pytest_asyncio

class ResourceNotInitialized(Exception):
    pass


class MyTestResource:
    def __init__(self) -> None:
        self.value = 42
        self.is_initialized = False
    
    async def init(self) -> None:
        print("MyTestResource.init")
        self.is_initialized = True

    async def show(self) -> None:
        if self.is_initialized:
            print(self.value)
        else:
            raise ResourceNotInitialized("Resource is not initialized")

    async def dispose(self) -> None:
        print("MyTestResource.dispose")
        self.is_initialized = False


@asynccontextmanager
async def my_test_resource() -> AsyncGenerator[MyTestResource, None]:
    resource = MyTestResource()
    await resource.init()
    try:
        print("context_manager.yield")
        yield resource
    finally:
        print("context_manager.finally")
        await resource.dispose()


class MyTestContainer(containers.DeclarativeContainer):
    resource: providers.Resource[MyTestResource] = providers.Resource(my_test_resource) # type: ignore


@pytest.mark.asyncio
async def test_container_resource_lifecycle() -> None:
    container = MyTestContainer()
    assert not container.resource.initialized
    
    container.resource.override(providers.Resource(my_test_resource))
    
    print("container.init_resources")
    await container.init_resources()
    assert not container.resource.initialized # Почему-то не инициализирован
    
    print("container.resource()")
    resource: MyTestResource = await container.resource.async_()
    
    print("container.shutdown_resources")
    await container.shutdown_resources()
    assert not container.resource.initialized
    
    print(resource)
    


