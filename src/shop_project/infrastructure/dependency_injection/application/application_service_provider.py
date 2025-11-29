from typing import Type

from dishka import Provider, Scope, provide

from shop_project.application.interfaces.interface_account_service import (
    IAccountService,
)
from shop_project.application.interfaces.interface_query_builder import IQueryBuilder
from shop_project.application.interfaces.interface_secret_service import ISecretService
from shop_project.application.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.application.services.customer_service import CustomerService
from shop_project.application.services.registration_service import RegistrationService


class ApplicationServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def customer_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> CustomerService:
        return CustomerService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
        )

    @provide
    async def register_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        account_service: IAccountService,
        secret_service: ISecretService,
    ) -> RegistrationService:
        return RegistrationService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            account_service=account_service,
            secret_service=secret_service,
        )
