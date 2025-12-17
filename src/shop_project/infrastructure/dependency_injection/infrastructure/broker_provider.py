from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator, Callable

from dishka import BaseScope, Component, Provider, Scope, provide
from taskiq import AsyncBroker


class BrokerProvider(Provider):
    scope = Scope.APP

    def __init__(
        self,
        database_ctx: Callable[[], AbstractAsyncContextManager[AsyncBroker]],
        *,
        scope: BaseScope | None = None,
        component: Component | None = None,
    ):
        super().__init__(scope, component)

        self.broker_ctx = database_ctx

    @provide(scope=Scope.APP)
    async def broker(self) -> AsyncGenerator[AsyncBroker, None]:
        ctx = self.broker_ctx()
        res = await ctx.__aenter__()  # вручную войти
        try:
            yield res
        finally:
            await ctx.__aexit__(None, None, None)
