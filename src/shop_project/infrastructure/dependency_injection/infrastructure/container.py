from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator, Callable

from dishka import BaseScope, Component, Provider, Scope, provide # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.unit_of_work import UnitOfWorkFactory



class InfrastructureProvider(Provider):
    scope = Scope.APP
    
    def __init__(self, database_ctx: Callable[[], AbstractAsyncContextManager[Database]], *, scope: BaseScope | None = None, component: Component | None = None):
        super().__init__(scope, component)
        
        self.database_ctx = database_ctx

    @provide(scope=Scope.APP)
    async def provide_database(self) -> AsyncGenerator[Database, None]:
        ctx = self.database_ctx()
        res = await ctx.__aenter__()  # вручную войти
        try:
            yield res
        finally:
            await ctx.__aexit__(None, None, None)
    
    @provide(scope=Scope.REQUEST)
    async def provide_session(self, db: Database) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession | None = None
        try:
            session = db.create_session()
            yield session
        finally:
            if session is not None:
                await session.close()
    
    @provide(scope=Scope.REQUEST)
    async def provide_unit_of_work(self, session: AsyncSession) -> UnitOfWorkFactory:
        return UnitOfWorkFactory(session)
        
        
        
        
        