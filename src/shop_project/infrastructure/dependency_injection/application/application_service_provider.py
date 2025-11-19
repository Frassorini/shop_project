from typing import Type

from dishka import Provider, Scope, provide  # type: ignore

from shop_project.application.interfaces.interface_query_builder import IQueryBuilder
from shop_project.application.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
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
