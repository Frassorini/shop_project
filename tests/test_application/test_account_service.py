from typing import Any, Awaitable, Callable, Coroutine, Type

import pytest
from dishka.async_container import AsyncContainer
from pydantic import SecretStr

from shop_project.application.authentication.commands.account_service import (
    AccountService,
)
from shop_project.application.authentication.schemas.credential_schema import (
    EmailTotpCredentialSchema,
    PasswordCredentialSchema,
    PhoneTotpCredentialSchema,
)
from shop_project.application.authentication.schemas.session_refresh_schema import (
    SessionRefreshSchema,
)
from shop_project.application.entities.account import Account
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.domain.entities.customer import Customer
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.subject import Subject
from shop_project.shared.phone_str import validate_phone_number
from tests.helpers import AggregateContainer


@pytest.mark.asyncio
async def test_account_service_add_password_auth(
    async_container: AsyncContainer,
    register_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    login_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    customer_container_factory: Callable[[], AggregateContainer],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
) -> None:
    customer_container: AggregateContainer = customer_container_factory()
    account_service = await async_container.get(AccountService)
    await save_container(customer_container)
    customer: Customer = (
        customer_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    account: Account = customer_container.dependencies[Account][0]

    access_payload = await get_subject_access_token_payload(customer)

    await account_service.add_login_password_auth(
        access_payload,
        PasswordCredentialSchema(
            identifier=account.login, password_plaintext=SecretStr("password")
        ),
    )

    refresh = await login_subject(Customer, password="password", login=account.login)

    assert refresh is not None


@pytest.mark.asyncio
async def test_account_service_add_sms_auth(
    async_container: AsyncContainer,
    register_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    login_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    customer_container_factory: Callable[[], AggregateContainer],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    totp_sms: Callable[[str], Awaitable[str]],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
) -> None:
    customer_container: AggregateContainer = customer_container_factory()
    phone_number = validate_phone_number("+79991234567")
    account_service = await async_container.get(AccountService)
    await save_container(customer_container)
    customer: Customer = (
        customer_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    account: Account = customer_container.dependencies[Account][0]
    code = await totp_sms(phone_number)

    access_payload = await get_subject_access_token_payload(customer)

    await account_service.add_phone_totp_auth(
        access_payload,
        PhoneTotpCredentialSchema(
            identifier=phone_number, code_plaintext=SecretStr(code)
        ),
    )

    refresh = await login_subject(Customer, phone_number=phone_number)

    assert refresh is not None


@pytest.mark.asyncio
async def test_account_service_add_email_auth(
    async_container: AsyncContainer,
    register_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    login_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    customer_container_factory: Callable[[], AggregateContainer],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    totp_email: Callable[[str], Awaitable[str]],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
) -> None:
    customer_container: AggregateContainer = customer_container_factory()
    email = "employee@example.com"
    account_service = await async_container.get(AccountService)
    await save_container(customer_container)
    customer: Customer = (
        customer_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    account: Account = customer_container.dependencies[Account][0]
    code = await totp_email(email)

    access_payload = await get_subject_access_token_payload(customer)

    await account_service.add_email_auth(
        access_payload,
        EmailTotpCredentialSchema(identifier=email, code_plaintext=SecretStr(code)),
    )

    refresh = await login_subject(Customer, email=email)

    assert refresh is not None
