from typing import Coroutine, Type
from uuid import uuid4

from plum import dispatch, overload

from shop_project.application.exceptions import (
    AlreadyExistsException,
    ForbiddenException,
)
from shop_project.application.interfaces.interface_account_service import (
    IAccountService,
)
from shop_project.application.interfaces.interface_query_builder import IQueryBuilder
from shop_project.application.interfaces.interface_session_service import (
    ISessionService,
)
from shop_project.application.interfaces.interface_totp_service import ITotpService
from shop_project.application.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.application.schemas.credential_schema import (
    CredentialSchema,
    EmailTotpCredentialSchema,
    LoginPasswordCredentialSchema,
    PhoneTotpCredentialSchema,
)
from shop_project.application.schemas.session_refresh_schema import SessionRefreshSchema
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.subject import Subject
from shop_project.infrastructure.entities.account import Account
from shop_project.infrastructure.entities.auth_session import AuthSession
from shop_project.infrastructure.entities.external_id_totp import ExternalIdTotp


class RegistrationService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        account_service: IAccountService,
        totp_service: ITotpService,
        session_service: ISessionService,
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type
        self._account_service: IAccountService = account_service
        self._totp_service: ITotpService = totp_service
        self._session_service: ISessionService = session_service

    async def register_customer(
        self, register_request: CredentialSchema
    ) -> SessionRefreshSchema:
        return await self._register_subject(Customer, register_request)

    async def register_employee(
        self, register_request: CredentialSchema
    ) -> SessionRefreshSchema:
        return await self._register_subject(Employee, register_request)

    async def register_manager(
        self, register_request: CredentialSchema
    ) -> SessionRefreshSchema:
        return await self._register_subject(Manager, register_request)

    async def _register_subject_sms(
        self, subject_type: Type[Subject], register_request: PhoneTotpCredentialSchema
    ) -> SessionRefreshSchema:
        subject = _create_subject(subject_type, register_request)
        account = self._account_service.create_account(
            subject, phone_number=register_request.identifier
        )

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Account)
            .from_attribute("phone_number", [register_request.identifier])
            .for_share()
            .load(ExternalIdTotp)
            .from_attribute("external_id", [register_request.identifier])
            .and_()
            .from_attribute("external_id_type", ["phone_number"])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resorces()
            if resources.get_all(Account):
                raise AlreadyExistsException

            totp = resources.get_one_by_attribute(
                ExternalIdTotp, "external_id", register_request.identifier
            )

            if not self._totp_service.verify_totp(
                totp, register_request.code_plaintext.get_secret_value()
            ):
                raise ForbiddenException

            auth_session, session_refresh = self._session_service.create_session(
                account, subject
            )
            resources.put(AuthSession, auth_session)
            resources.put(Account, account)
            resources.put(subject_type, subject)
            resources.delete(ExternalIdTotp, totp)

            uow.mark_commit()

        return SessionRefreshSchema.model_validate(
            session_refresh, from_attributes=True
        )

    async def _register_subject_email(
        self, subject_type: Type[Subject], register_request: EmailTotpCredentialSchema
    ) -> SessionRefreshSchema:
        subject = _create_subject(subject_type, register_request)
        account = self._account_service.create_account(
            subject, email=register_request.identifier
        )

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Account)
            .from_attribute("email", [register_request.identifier])
            .for_share()
            .load(ExternalIdTotp)
            .from_attribute("external_id", [register_request.identifier])
            .and_()
            .from_attribute("external_id_type", ["email"])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resorces()
            if resources.get_all(Account):
                raise AlreadyExistsException

            totp = resources.get_one_by_attribute(
                ExternalIdTotp, "external_id", register_request.identifier
            )

            if not self._totp_service.verify_totp(
                totp, register_request.code_plaintext.get_secret_value()
            ):
                raise ForbiddenException

            auth_session, session_refresh = self._session_service.create_session(
                account, subject
            )
            resources.put(AuthSession, auth_session)
            resources.put(Account, account)
            resources.put(subject_type, subject)
            resources.delete(ExternalIdTotp, totp)

            uow.mark_commit()

        return SessionRefreshSchema.model_validate(
            session_refresh, from_attributes=True
        )

    async def _register_subject_login(
        self,
        subject_type: Type[Subject],
        register_request: LoginPasswordCredentialSchema,
    ) -> SessionRefreshSchema:
        subject = _create_subject(subject_type, register_request)
        account = self._account_service.create_account(
            subject, login=register_request.identifier
        )
        self._account_service.set_password(
            account, register_request.password_plaintext.get_secret_value()
        )

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Account)
            .from_attribute("login", [register_request.identifier])
            .for_share()
            .build()
        ) as uow:
            resources = uow.get_resorces()

            if resources.get_all(Account):
                raise AlreadyExistsException

            auth_session, session_refresh = self._session_service.create_session(
                account, subject
            )
            resources.put(AuthSession, auth_session)
            resources.put(Account, account)
            resources.put(subject_type, subject)

            uow.mark_commit()

        return SessionRefreshSchema.model_validate(
            session_refresh, from_attributes=True
        )

    @overload
    def _register_subject(
        self,
        subject_type: Type[Subject],
        register_request: LoginPasswordCredentialSchema,
    ) -> Coroutine[None, None, SessionRefreshSchema]:
        return self._register_subject_login(subject_type, register_request)

    @overload
    def _register_subject(
        self, subject_type: Type[Subject], register_request: EmailTotpCredentialSchema
    ) -> Coroutine[None, None, SessionRefreshSchema]:
        return self._register_subject_email(subject_type, register_request)

    @overload
    def _register_subject(
        self, subject_type: Type[Subject], register_request: PhoneTotpCredentialSchema
    ) -> Coroutine[None, None, SessionRefreshSchema]:
        return self._register_subject_sms(subject_type, register_request)

    @overload
    def _register_subject(
        self, subject_type: Type[Subject], register_request: CredentialSchema
    ) -> Coroutine[None, None, SessionRefreshSchema]:
        raise NotImplementedError

    @dispatch
    def _register_subject(
        self, subject_type: Type[Subject], register_request: CredentialSchema
    ) -> Coroutine[None, None, SessionRefreshSchema]: ...


@overload
def _create_subject(
    subject_type: Type[Employee], register_request: CredentialSchema
) -> Employee:
    return Employee(
        entity_id=uuid4(),
        name="Name",
    )


@overload
def _create_subject(
    subject_type: Type[Manager], register_request: CredentialSchema
) -> Manager:
    return Manager(
        entity_id=uuid4(),
        name="Name",
    )


@overload
def _create_subject(
    subject_type: Type[Customer], register_request: CredentialSchema
) -> Customer:
    return Customer(
        entity_id=uuid4(),
        name="Name",
    )


@overload
def _create_subject(
    subject_type: Type[Subject], register_request: CredentialSchema
) -> Subject:
    raise NotImplementedError


@dispatch
def _create_subject(
    subject_type: Type[Subject], register_request: CredentialSchema
) -> Subject: ...
