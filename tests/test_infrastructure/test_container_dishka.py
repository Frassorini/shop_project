import pytest
import pytest_asyncio
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import AsyncGenerator, Awaitable, Callable

from dishka import BaseScope, Component, make_async_container, make_container, Provider, provide, Scope # type: ignore

class ResourceNotInitialized(Exception):
    pass

class MyTestResource:
    def __init__(self) -> None:
        self.value = 42
        self.is_initialized = False
    
    async def init(self) -> None:
        # print("MyTestResource.init")
        self.is_initialized = True

    async def show(self) -> None:
        if self.is_initialized:
            pass
            # print(self.value)
        else:
            raise ResourceNotInitialized("Resource is not initialized")

    async def dispose(self) -> None:
        # print("MyTestResource.dispose")
        self.is_initialized = False

@asynccontextmanager
async def my_test_resource() -> AsyncGenerator[MyTestResource, None]:
    resource = MyTestResource()
    await resource.init()
    try:
        # print("context_manager.yield")
        yield resource
    finally:
        # print("context_manager.finally")
        await resource.dispose()


class MyProvider(Provider):
    scope = Scope.APP
    
    def __init__(self, database_ctx: Callable[[], AbstractAsyncContextManager[MyTestResource]], *, scope: BaseScope | None = None, component: Component | None = None):
        super().__init__(scope, component)
        
        self.database_ctx = database_ctx
        

    @provide(scope=Scope.APP)
    async def provide_resource(self) -> AsyncGenerator[MyTestResource, None]:
        ctx = self.database_ctx()
        res = await ctx.__aenter__()  # вручную войти
        try:
            # print("MyProvider.provide_resource.yield")
            yield res
        finally:
            # print("MyProvider.provide_resource.finally")
            await ctx.__aexit__(None, None, None)



@pytest.mark.asyncio
async def test_resource_lifecycle():
    container = make_async_container(MyProvider(my_test_resource))
    async with container() as ctx:
        resource = await ctx.get(MyTestResource)
        assert resource.is_initialized is True
        await resource.show()

