from typing import Awaitable, Callable, Type

import pytest
from dishka.async_container import AsyncContainer
from pydantic import SecretStr

from shop_project.application.authentication.commands.authentication_service import (
    AuthenticationService,
)
from shop_project.application.authentication.schemas.credential_schema import (
    CredentialSchema,
    EmailPasswordCredentialSchema,
    EmailTotpCredentialSchema,
    LoginPasswordCredentialSchema,
    PhonePasswordCredentialSchema,
    PhoneTotpCredentialSchema,
)
from shop_project.application.authentication.schemas.session_refresh_schema import (
    SessionRefreshSchema,
)
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.subject import Subject


@pytest.fixture
def login_subject(
    async_container: AsyncContainer,
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

        totp = False
        if (email or phone_number) and not password:
            totp = True

        if (email or phone_number) and password:
            raise ValueError(
                "Email or phone number and password can't be used together"
            )

        authentication_service = await async_container.get(AuthenticationService)

        request: CredentialSchema | None = None

        if phone_number and totp:
            totp_sms_code = await totp_sms(phone_number)
            request = PhoneTotpCredentialSchema(
                identifier=phone_number,
                code_plaintext=SecretStr(totp_sms_code),
            )
        if email and totp:
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
        if phone_number and not totp:
            assert password
            request = PhonePasswordCredentialSchema(
                identifier=phone_number,
                password_plaintext=SecretStr(password),
            )
        if email and not totp:
            assert password
            request = EmailPasswordCredentialSchema(
                identifier=email,
                password_plaintext=SecretStr(password),
            )

        if not request:
            raise ValueError("Request couldn't be created")

        if subject_type == Manager:
            refresh = await authentication_service.login_manager(request)
        elif subject_type == Employee:
            refresh = await authentication_service.login_employee(request)
        elif subject_type == Customer:
            refresh = await authentication_service.login_customer(request)
        else:
            raise ValueError("Invalid subject type")

        return refresh

    return _inner
