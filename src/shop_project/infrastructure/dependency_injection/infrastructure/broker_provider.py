from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING, AsyncGenerator, Callable

from dishka import BaseScope, Component, Provider, Scope, provide # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.message_broker.broker_container import BrokerContainer
from shop_project.infrastructure.unit_of_work import UnitOfWorkFactory


class BrokerProvider(Provider):
    scope = Scope.APP
    
    def __init__(self, database_ctx: Callable[[], AbstractAsyncContextManager[BrokerContainer]], *, scope: BaseScope | None = None, component: Component | None = None):
        super().__init__(scope, component)
        
        self.broker_ctx = database_ctx

    @provide(scope=Scope.APP)
    async def provide_broker(self) -> AsyncGenerator[BrokerContainer, None]:
        ctx = self.broker_ctx()
        res = await ctx.__aenter__()  # вручную войти
        try:
            yield res
        finally:
            await ctx.__aexit__(None, None, None)
