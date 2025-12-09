from typing import Coroutine, Type

from plum import dispatch, overload

from shop_project.application.exceptions import (
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
    EmailPasswordCredentialSchema,
    EmailTotpCredentialSchema,
    LoginPasswordCredentialSchema,
    PasswordCredentialSchema,
    PhonePasswordCredentialSchema,
    PhoneTotpCredentialSchema,
    TotpCredentialSchema,
)
from shop_project.application.schemas.session_refresh_schema import SessionRefreshSchema
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.subject import Subject
from shop_project.infrastructure.entities.account import Account
from shop_project.infrastructure.entities.auth_session import AuthSession
from shop_project.infrastructure.entities.external_id_totp import ExternalIdTotp


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

    async def _refresh_session(self, subject_type: Type[Subject], refresh_token: str):
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
            resources = uow.get_resorces()
            auth_session = resources.get_one_by_attribute(
                AuthSession, "refresh_token_fingerprint", refresh_token
            )
            subject = resources.get_by_id(subject_type, auth_session.account_id)

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
            resources = uow.get_resorces()

            if not resources.get_all(Account) or not resources.get_all(subject_type):
                raise ForbiddenException

            account = resources.get_one_by_attribute(
                Account, external_id_type, external_id
            )
            subject = resources.get_by_id(subject_type, account.entity_id)

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
            resources = uow.get_resorces()
            if not resources.get_all(Account):
                raise ForbiddenException

            if not resources.get_all(ExternalIdTotp):
                raise ForbiddenException

            if not resources.get_all(subject_type):
                raise ForbiddenException

            account = resources.get_one_by_attribute(
                Account, external_id_type, external_id
            )
            totp = resources.get_one_by_attribute(
                ExternalIdTotp, "external_id", external_id
            )
            subject = resources.get_by_id(subject_type, account.entity_id)

            if not self._totp_service.verify_totp(
                totp, credential.code_plaintext.get_secret_value()
            ):
                raise ForbiddenException

            resources.delete(ExternalIdTotp, totp)

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
