from typing import Coroutine, Type
from uuid import uuid4

from plum import dispatch, overload

from shop_project.application.authentication.schemas.credential_schema import (
    CredentialSchema,
    EmailTotpCredentialSchema,
    LoginPasswordCredentialSchema,
    PhoneTotpCredentialSchema,
)
from shop_project.application.authentication.schemas.session_refresh_schema import (
    SessionRefreshSchema,
)
from shop_project.application.authentication.shared_scenarios import (
    verify_and_consume_totp,
)
from shop_project.application.entities.account import Account
from shop_project.application.entities.auth_session import AuthSession
from shop_project.application.entities.external_id_totp import ExternalIdTotp
from shop_project.application.exceptions import (
    ApplicationAlreadyExistsError,
)
from shop_project.application.shared.interfaces.interface_account_service import (
    IAccountService,
)
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_resource_container import (
    IResourceContainer,
)
from shop_project.application.shared.interfaces.interface_session_service import (
    ISessionService,
)
from shop_project.application.shared.interfaces.interface_totp_service import (
    ITotpService,
)
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.helpers.subject_mapper import get_subject
from shop_project.domain.interfaces.subject import Subject, SubjectEnum
from shop_project.infrastructure.env_loader import get_env


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

    async def register_env(
        self, register_request: CredentialSchema
    ) -> SessionRefreshSchema:
        subject_type = get_subject(SubjectEnum(get_env("SUBJECT_MODE")))
        return await self._register_subject(subject_type, register_request)

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
            resources = uow.get_resources()

            _ensure_account_not_exists(resources)

            verify_and_consume_totp(
                resources=resources,
                totp_service=self._totp_service,
                external_id=register_request.identifier,
                code=register_request.code_plaintext.get_secret_value(),
            )

            session_refresh = self._make_registration(
                resources=resources,
                subject_type=subject_type,
                identidier_type="phone_number",
                register_request=register_request,
            )

            uow.mark_commit()

        return session_refresh

    async def _register_subject_email(
        self, subject_type: Type[Subject], register_request: EmailTotpCredentialSchema
    ) -> SessionRefreshSchema:
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
            resources = uow.get_resources()
            _ensure_account_not_exists(resources)

            verify_and_consume_totp(
                resources=resources,
                totp_service=self._totp_service,
                external_id=register_request.identifier,
                code=register_request.code_plaintext.get_secret_value(),
            )

            session_refresh = self._make_registration(
                resources=resources,
                subject_type=subject_type,
                identidier_type="email",
                register_request=register_request,
            )

            uow.mark_commit()

        return session_refresh

    async def _register_subject_login(
        self,
        subject_type: Type[Subject],
        register_request: LoginPasswordCredentialSchema,
    ) -> SessionRefreshSchema:

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Account)
            .from_attribute("login", [register_request.identifier])
            .for_share()
            .build()
        ) as uow:
            resources = uow.get_resources()

            _ensure_account_not_exists(resources)

            session_refresh = self._make_registration(
                resources=resources,
                subject_type=subject_type,
                identidier_type="login",
                register_request=register_request,
            )

            account = _get_account_by_identifier(
                resources=resources, login=register_request.identifier
            )

            if not account:
                raise RuntimeError

            self._account_service.set_password(
                account, register_request.password_plaintext.get_secret_value()
            )

            uow.mark_commit()

        return SessionRefreshSchema.model_validate(
            session_refresh, from_attributes=True
        )

    def _make_registration(
        self,
        resources: IResourceContainer,
        subject_type: Type[Subject],
        identidier_type: str,
        register_request: CredentialSchema,
    ) -> SessionRefreshSchema:
        subject = _create_subject(subject_type, register_request)

        if identidier_type not in ["login", "phone_number", "email"]:
            raise ValueError

        account = self._account_service.create_account(
            subject,
            login=register_request.identifier if identidier_type == "login" else None,
            phone_number=(
                register_request.identifier
                if identidier_type == "phone_number"
                else None
            ),
            email=register_request.identifier if identidier_type == "email" else None,
        )
        auth_session, session_refresh = self._session_service.create_session(
            account, subject
        )
        resources.put(AuthSession, auth_session)
        resources.put(Account, account)
        resources.put(subject_type, subject)

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


def _ensure_account_not_exists(resources: IResourceContainer) -> None:
    if resources.get_all(Account):
        raise ApplicationAlreadyExistsError("Account already exists")


def _get_account_by_identifier(
    resources: IResourceContainer,
    phone_number: str | None = None,
    email: str | None = None,
    login: str | None = None,
) -> Account | None:
    if not (bool(phone_number) + bool(email) + bool(login) == 1):
        raise ValueError("Exactly one identifier must be provided")
    if phone_number:
        return resources.get_one_or_none_by_attribute(
            Account, "phone_number", phone_number
        )
    if email:
        return resources.get_one_or_none_by_attribute(Account, "email", email)
    if login:
        return resources.get_one_or_none_by_attribute(Account, "login", login)


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
