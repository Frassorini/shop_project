from typing import Awaitable, Callable, Type

import pytest
from dishka.async_container import AsyncContainer
from pydantic import SecretStr

from shop_project.application.schemas.credential_schema import (
    CredentialSchema,
    EmailTotpCredentialSchema,
    LoginPasswordCredentialSchema,
    PhoneTotpCredentialSchema,
)
from shop_project.application.schemas.session_refresh_schema import SessionRefreshSchema
from shop_project.application.services.registration_service import RegistrationService
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.subject import Subject
from shop_project.infrastructure.persistence.unit_of_work import UnitOfWorkFactory


@pytest.fixture
def register_subject(
    async_container: AsyncContainer,
    uow_factory: UnitOfWorkFactory,
    totp_sms: Callable[[str], Awaitable[str]],
    totp_email: Callable[[str], Awaitable[str]],
) -> Callable[..., Awaitable[SessionRefreshSchema]]:
    async def _inner(
        subject_type: Type[Subject],
        *,
        phone_number: str | None = None,
        email: str | None = None,
        login: str | None = None,
        password: str | None = None,
    ) -> SessionRefreshSchema:
        if not sum(bool(x) for x in [phone_number, email, login]) == 1:
            raise ValueError
        if login and not password:
            raise ValueError

        register_service = await async_container.get(RegistrationService)

        request: CredentialSchema | None = None

        if phone_number:
            totp_sms_code = await totp_sms(phone_number)
            request = PhoneTotpCredentialSchema(
                identifier=phone_number,
                code_plaintext=SecretStr(totp_sms_code),
            )
        if email:
            totp_email_code = await totp_email(email)
            request = EmailTotpCredentialSchema(
                identifier=email,
                code_plaintext=SecretStr(totp_email_code),
            )
        if login:
            assert password
            request = LoginPasswordCredentialSchema(
                identifier=login,
                password_plaintext=SecretStr(password),
            )

        if not request:
            raise ValueError

        if subject_type == Manager:
            refresh = await register_service.register_manager(request)
        elif subject_type == Employee:
            refresh = await register_service.register_employee(request)
        elif subject_type == Customer:
            refresh = await register_service.register_customer(request)
        else:
            raise ValueError

        return refresh

    return _inner
