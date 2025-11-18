from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator, Callable, Type

from dishka import BaseScope, Component, Provider, Scope, provide, alias # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.application.interfaces.interface_query_builder import IQueryBuilder
from shop_project.application.interfaces.interface_unit_of_work import IUnitOfWorkFactory
from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.unit_of_work import UnitOfWorkFactory

from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.application.services.customer_service import CustomerService

class ApplicationServiceProvider(Provider):
    scope = Scope.REQUEST
    
    @provide
    async def customer_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> CustomerService:
        return CustomerService(unit_of_work_factory, query_builder_type)
