from typing import Type

from shop_project.application.authentication.schemas.credential_schema import (
    EmailTotpCredentialSchema,
    PasswordCredentialSchema,
    PhoneTotpCredentialSchema,
)
from shop_project.application.authentication.shared_scenarios import (
    verify_and_consume_totp,
)
from shop_project.application.entities.account import Account
from shop_project.application.entities.external_id_totp import ExternalIdTotp
from shop_project.application.exceptions import (
    ApplicationForbiddenError,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.interfaces.interface_account_service import (
    IAccountService,
)
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
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
from shop_project.application.shared.scenarios.entity import get_one_or_raise_forbidden


class AccountService:
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

    async def add_login_password_auth(
        self, access_payload: AccessTokenPayload, password: PasswordCredentialSchema
    ) -> None:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Account)
            .from_id([access_payload.account_id])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()

            account = get_one_or_raise_forbidden(
                resources, Account, access_payload.account_id
            )

            if not account.login:
                account.login = password.identifier
            elif account.login != password.identifier:
                raise ApplicationForbiddenError("Login mismatch")

            self._account_service.set_password(
                account, password.password_plaintext.get_secret_value()
            )

            uow.mark_commit()

    async def add_phone_totp_auth(
        self,
        access_payload: AccessTokenPayload,
        phone_schema: PhoneTotpCredentialSchema,
    ) -> None:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Account)
            .from_id([access_payload.account_id])
            .for_update()
            .load(ExternalIdTotp)
            .from_attribute("external_id", [phone_schema.identifier])
            .and_()
            .from_attribute("external_id_type", ["phone_number"])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()

            account = get_one_or_raise_forbidden(
                resources, Account, access_payload.account_id
            )

            verify_and_consume_totp(
                resources=resources,
                totp_service=self._totp_service,
                external_id=phone_schema.identifier,
                code=phone_schema.code_plaintext.get_secret_value(),
            )

            account.phone_number = phone_schema.identifier

            uow.mark_commit()

    async def add_email_auth(
        self,
        access_payload: AccessTokenPayload,
        email_schema: EmailTotpCredentialSchema,
    ):
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Account)
            .from_id([access_payload.account_id])
            .for_update()
            .load(ExternalIdTotp)
            .from_attribute("external_id", [email_schema.identifier])
            .and_()
            .from_attribute("external_id_type", ["email"])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()

            account = get_one_or_raise_forbidden(
                resources, Account, access_payload.account_id
            )

            verify_and_consume_totp(
                resources=resources,
                totp_service=self._totp_service,
                external_id=email_schema.identifier,
                code=email_schema.code_plaintext.get_secret_value(),
            )

            account.email = email_schema.identifier

            uow.mark_commit()
