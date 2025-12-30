from typing import Coroutine, Type, TypeVar

from plum import dispatch, overload

from shop_project.application.authentication.schemas.credential_schema import (
    CredentialSchema,
    EmailPasswordCredentialSchema,
    EmailTotpCredentialSchema,
    LoginPasswordCredentialSchema,
    PasswordCredentialSchema,
    PhonePasswordCredentialSchema,
    PhoneTotpCredentialSchema,
    TotpCredentialSchema,
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
    ForbiddenException,
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


class AuthenticationService:
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

    async def login_env(self, credential: CredentialSchema):
        subject_type = get_subject(SubjectEnum(get_env("SUBJECT_MODE")))
        return await self._login_subject(subject_type, credential)

    async def refresh_session_env(self, refresh_token: str):
        subject_type = get_subject(SubjectEnum(get_env("SUBJECT_MODE")))
        return await self._refresh_session(subject_type, refresh_token)

    async def login_customer(self, credential: CredentialSchema):
        return await self._login_subject(Customer, credential)

    async def login_employee(self, credential: CredentialSchema):
        return await self._login_subject(Employee, credential)

    async def login_manager(self, credential: CredentialSchema):
        return await self._login_subject(Manager, credential)

    async def refresh_session_customer(self, refresh_token: str):
        return await self._refresh_session(Customer, refresh_token)

    async def refresh_session_employee(self, refresh_token: str):
        return await self._refresh_session(Employee, refresh_token)

    async def refresh_session_manager(self, refresh_token: str):
        return await self._refresh_session(Manager, refresh_token)

    async def _refresh_session(
        self, subject_type: Type[Subject], refresh_token: str
    ) -> SessionRefreshSchema:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(AuthSession)
            .from_attribute("refresh_token_fingerprint", [refresh_token])
            .for_update()
            .load(subject_type)
            .from_previous(0)
            .for_share()
            .build()
        ) as uow:
            resources = uow.get_resources()

            auth_session = _get_one_auth_session_or_abort(resources)
            subject = _get_one_subject_or_abort(resources, subject_type)

            session_refresh = self._session_service.refresh_session(
                subject, auth_session
            )
            uow.mark_commit()

        return SessionRefreshSchema.model_validate(
            session_refresh, from_attributes=True
        )

    async def _authenticate_password(
        self, subject_type: Type[Subject], credential: PasswordCredentialSchema
    ) -> SessionRefreshSchema:
        external_id, external_id_type = _extract_external_id_and_type(credential)

        print(subject_type)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Account)
            .from_attribute(external_id_type, [external_id])
            .for_share()
            .load(subject_type)
            .from_previous(0)
            .for_share()
            .build()
        ) as uow:
            resources = uow.get_resources()

            account = _get_one_account_or_abort(resources)
            subject = _get_one_subject_or_abort(resources, subject_type)

            if not self._account_service.verify_password(
                account, credential.password_plaintext.get_secret_value()
            ):
                raise ForbiddenException

            auth_session, session_refresh = self._session_service.create_session(
                account, subject
            )
            resources.put(AuthSession, auth_session)

            uow.mark_commit()

        return SessionRefreshSchema.model_validate(
            session_refresh, from_attributes=True
        )

    async def _authenticate_totp(
        self, subject_type: Type[Subject], credential: TotpCredentialSchema
    ) -> SessionRefreshSchema:
        external_id, external_id_type = _extract_external_id_and_type(credential)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Account)
            .from_attribute(external_id_type, [external_id])
            .for_share()
            .load(ExternalIdTotp)
            .from_attribute("external_id", [external_id])
            .and_()
            .from_attribute("external_id_type", [external_id_type])
            .for_update()
            .load(subject_type)
            .from_previous(0)
            .for_share()
            .build()
        ) as uow:
            resources = uow.get_resources()

            account = _get_one_account_or_abort(resources)
            subject = _get_one_subject_or_abort(resources, subject_type)

            verify_and_consume_totp(
                resources=resources,
                totp_service=self._totp_service,
                external_id=external_id,
                code=credential.code_plaintext.get_secret_value(),
            )

            auth_session, session_refresh = self._session_service.create_session(
                account, subject
            )
            resources.put(AuthSession, auth_session)

            uow.mark_commit()

        return SessionRefreshSchema.model_validate(
            session_refresh, from_attributes=True
        )

    @overload
    def _login_subject(
        self, subject_type: Type[Subject], credential: TotpCredentialSchema
    ) -> Coroutine[None, None, SessionRefreshSchema]:
        return self._authenticate_totp(subject_type, credential)

    @overload
    def _login_subject(
        self, subject_type: Type[Subject], credential: PasswordCredentialSchema
    ) -> Coroutine[None, None, SessionRefreshSchema]:
        return self._authenticate_password(subject_type, credential)

    @overload
    def _login_subject(
        self, subject_type: Type[Subject], credential: CredentialSchema
    ) -> Coroutine[None, None, SessionRefreshSchema]:
        raise NotImplementedError

    @dispatch
    def _login_subject(
        self, subject_type: Type[Subject], credential: CredentialSchema
    ) -> Coroutine[None, None, SessionRefreshSchema]: ...


S = TypeVar("S", bound=Subject)


def _get_one_subject_or_abort(
    resources: IResourceContainer, subject_type: Type[S]
) -> S:
    subjects = resources.get_all(subject_type)
    if not subjects:
        raise ForbiddenException
    if len(subjects) > 1:
        raise RuntimeError

    return subjects[0]


def _get_one_account_or_abort(resources: IResourceContainer) -> Account:
    accounts = resources.get_all(Account)
    if not accounts:
        raise ForbiddenException
    if len(accounts) > 1:
        raise RuntimeError

    return accounts[0]


def _get_one_auth_session_or_abort(resources: IResourceContainer) -> AuthSession:
    auth_sessions = resources.get_all(AuthSession)
    if not auth_sessions:
        raise ForbiddenException
    if len(auth_sessions) > 1:
        raise RuntimeError

    return auth_sessions[0]


@overload
def _extract_external_id_and_type(
    credential: LoginPasswordCredentialSchema,
) -> tuple[str, str]:
    return credential.identifier, "login"


@overload
def _extract_external_id_and_type(
    credential: PhonePasswordCredentialSchema,
) -> tuple[str, str]:
    return credential.identifier, "phone_number"


@overload
def _extract_external_id_and_type(
    credential: EmailPasswordCredentialSchema,
) -> tuple[str, str]:
    return credential.identifier, "email"


@overload
def _extract_external_id_and_type(
    credential: PhoneTotpCredentialSchema,
) -> tuple[str, str]:
    return credential.identifier, "phone_number"


@overload
def _extract_external_id_and_type(
    credential: EmailTotpCredentialSchema,
) -> tuple[str, str]:
    return credential.identifier, "email"


@overload
def _extract_external_id_and_type(credential: CredentialSchema) -> tuple[str, str]:
    raise NotImplementedError


@dispatch
def _extract_external_id_and_type(credential: CredentialSchema) -> tuple[str, str]: ...
