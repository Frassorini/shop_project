import pytest
import pytest_asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dishka import make_async_container, make_container, Provider, provide, Scope

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


class MyProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.APP)
    async def provide_resource(self) -> AsyncGenerator[MyTestResource, None]:
        ctx = my_test_resource()
        res = await ctx.__aenter__()  # вручную войти
        try:
            print("MyProvider.provide_resource.yield")
            yield res
        finally:
            print("MyProvider.provide_resource.finally")
            await ctx.__aexit__(None, None, None)



@pytest.mark.asyncio
async def test_resource_lifecycle():
    container = make_async_container(MyProvider())
    async with container() as ctx:
        resource = await ctx.get(MyTestResource)
        assert resource.is_initialized is True
        await resource.show()
    # после выхода из контекста ресурс должен быть освобождён
    assert resource.is_initialized is True
    1 / 0
