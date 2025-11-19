from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator, Callable

from dishka import BaseScope, Component, Provider, Scope, provide  # type: ignore

from shop_project.infrastructure.message_broker.broker_container import BrokerContainer


class BrokerProvider(Provider):
    scope = Scope.APP

    def __init__(
        self,
        database_ctx: Callable[[], AbstractAsyncContextManager[BrokerContainer]],
        *,
        scope: BaseScope | None = None,
        component: Component | None = None,
    ):
        super().__init__(scope, component)

        self.broker_ctx = database_ctx

    @provide(scope=Scope.APP)
    async def broker(self) -> AsyncGenerator[BrokerContainer, None]:
        ctx = self.broker_ctx()
        res = await ctx.__aenter__()  # вручную войти
        try:
            yield res
        finally:
            await ctx.__aexit__(None, None, None)
