from typing import Type
from uuid import uuid4

from plum import dispatch, overload

from shop_project.application.exceptions import AlreadyExistsException
from shop_project.application.interfaces.interface_account_service import (
    IAccountService,
)
from shop_project.application.interfaces.interface_query_builder import IQueryBuilder
from shop_project.application.interfaces.interface_secret_service import ISecretService
from shop_project.application.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.application.schemas.register_request_schema import (
    EmailRegisterRequestSchema,
    LoginRegisterRequestSchema,
    PhoneRegisterRequestSchema,
    RegisterRequestSchema,
)
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.subject import Subject
from shop_project.infrastructure.authentication.helpers.credential import Credential
from shop_project.infrastructure.entities.account import Account
from shop_project.infrastructure.entities.secret import AuthType, Secret


class RegistrationService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        account_service: IAccountService,
        secret_service: ISecretService,
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type
        self._account_service: IAccountService = account_service
        self._secret_service: ISecretService = secret_service

    async def register_customer(self, register_request: RegisterRequestSchema) -> None:
        return await self._register_subject(
            subject_type=Customer, register_request=register_request
        )

    async def register_employee(self, register_request: RegisterRequestSchema) -> None:
        return await self._register_subject(
            subject_type=Employee, register_request=register_request
        )

    async def register_manager(self, register_request: RegisterRequestSchema) -> None:
        return await self._register_subject(
            subject_type=Manager, register_request=register_request
        )

    async def _register_subject(
        self, subject_type: Type[Subject], register_request: RegisterRequestSchema
    ) -> None:
        subject = _create_subject(subject_type, register_request)
        account = self._create_account(subject, register_request)
        secret = self._secret_service.create_secret(
            account_id=account.entity_id,
            credential=Credential(
                auth_type=AuthType.PASSWORD,
                payload={"password": register_request.credential},
            ),
        )

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Account)
            .from_attribute("phone_number", [register_request.identifier])
            .for_share()
            .build()
        ) as uow:
            resources = uow.get_resorces()

            if resources.get_all(Account):
                raise AlreadyExistsException

            resources.put(Account, account)
            resources.put(subject_type, subject)
            resources.put(Secret, secret)
            uow.mark_commit()

    @overload
    def _create_account(
        self, subject: Subject, register_request: PhoneRegisterRequestSchema
    ) -> Account:
        return self._account_service.create_account(
            subject=subject,
            phone_number=register_request.identifier,
        )

    @overload
    def _create_account(
        self, subject: Subject, register_request: LoginRegisterRequestSchema
    ) -> Account:
        return self._account_service.create_account(
            subject=subject,
            login=register_request.identifier,
        )

    @overload
    def _create_account(
        self, subject: Subject, register_request: EmailRegisterRequestSchema
    ) -> Account:
        return self._account_service.create_account(
            subject=subject,
            email=register_request.identifier,
        )

    @overload
    def _create_account(
        self, subject: Subject, register_request: RegisterRequestSchema
    ) -> Account:
        raise NotImplementedError

    @dispatch
    def _create_account(
        self, subject: Subject, register_request: RegisterRequestSchema
    ) -> Account: ...


@overload
def _create_subject(
    subject_type: Type[Employee], register_request: RegisterRequestSchema
) -> Employee:
    return Employee(
        entity_id=uuid4(),
        name="Name",
    )


@overload
def _create_subject(
    subject_type: Type[Manager], register_request: RegisterRequestSchema
) -> Manager:
    return Manager(
        entity_id=uuid4(),
        name="Name",
    )


@overload
def _create_subject(
    subject_type: Type[Customer], register_request: RegisterRequestSchema
) -> Customer:
    return Customer(
        entity_id=uuid4(),
        name="Name",
    )


@overload
def _create_subject(
    subject_type: Type[Subject], register_request: RegisterRequestSchema
) -> Subject:
    raise NotImplementedError


@dispatch
def _create_subject(
    subject_type: Type[Subject], register_request: RegisterRequestSchema
) -> Subject: ...
