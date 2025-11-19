from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator, Callable, Type

from dishka import BaseScope, Component, Provider, Scope, provide, alias # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.application.interfaces.interface_query_builder import IQueryBuilder
from shop_project.application.interfaces.interface_unit_of_work import IUnitOfWorkFactory
from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.unit_of_work import UnitOfWorkFactory

from shop_project.infrastructure.query.query_builder import QueryBuilder

class DatabaseProvider(Provider):
    scope = Scope.APP
    
    def __init__(self, database_ctx: Callable[[], AbstractAsyncContextManager[Database]], *, scope: BaseScope | None = None, component: Component | None = None):
        super().__init__(scope, component)
        
        self.database_ctx = database_ctx

    @provide(scope=Scope.APP)
    async def database(self) -> AsyncGenerator[Database, None]:
        ctx = self.database_ctx()
        res = await ctx.__aenter__()  # вручную войти
        try:
            yield res
        finally:
            await ctx.__aexit__(None, None, None)
    
    @provide(scope=Scope.REQUEST)
    async def session(self, db: Database) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession | None = None
        try:
            session = db.create_session()
            yield session
        finally:
            if session is not None:
                await session.close()
    
    @provide(scope=Scope.REQUEST)
    async def unit_of_work_factory(self, database: Database) -> UnitOfWorkFactory:
        return UnitOfWorkFactory(database)
        
    @provide(scope=Scope.APP)
    async def query_builder_type(self) -> Type[QueryBuilder]:
        return QueryBuilder
    
    query_builder_type_proto = alias(Type[QueryBuilder], provides=Type[IQueryBuilder])
    unit_of_work_proto = alias(UnitOfWorkFactory, provides=IUnitOfWorkFactory)
