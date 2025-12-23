from typing import Awaitable, Callable, Type, cast

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.dto.mapper import to_dto
from shop_project.application.interfaces.interface_session_service import (
    ISessionService,
)
from shop_project.application.schemas.session_refresh_schema import SessionRefreshSchema
from shop_project.application.services.authentication_service import (
    AuthenticationService,
)
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.authentication.helpers.access_token_payload import (
    AccessTokenPayload,
)
from shop_project.infrastructure.entities.auth_session import AuthSession
from shop_project.shared.phone_str import validate_phone_number


@pytest.mark.asyncio
async def test_auth_customer_sms_code_flow(
    async_container: AsyncContainer,
    register_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    login_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, str], Awaitable[PersistableEntity]
    ],
) -> None:
    session_service = await async_container.get(ISessionService)
    phone_number = validate_phone_number("+79991234567")

    refresh_before = await register_subject(Customer, phone_number=phone_number)
    refresh_fingerprint_before = session_service.get_refresh_token_fingerprint(
        refresh_before.refresh_token.get_secret_value()
    )
    auth_session_before: AuthSession = cast(
        AuthSession,
        await uow_get_one_single_model(
            AuthSession, "refresh_token_fingerprint", refresh_fingerprint_before
        ),
    )
    auth_session_snapshot_before = to_dto(auth_session_before)

    refresh_new = await login_subject(Customer, phone_number=phone_number)
    refresh_fingerprint_after = session_service.get_refresh_token_fingerprint(
        refresh_new.refresh_token.get_secret_value()
    )
    auth_session_after: AuthSession = cast(
        AuthSession,
        await uow_get_one_single_model(
            AuthSession, "refresh_token_fingerprint", refresh_fingerprint_after
        ),
    )
    auth_session_snapshot_after = to_dto(auth_session_after)

    assert (
        auth_session_snapshot_before.expiration
        <= auth_session_snapshot_after.expiration
    )
    assert (
        auth_session_snapshot_before.account_id
        == auth_session_snapshot_after.account_id
    )


@pytest.mark.asyncio
async def test_auth_employee_email_code_flow(
    async_container: AsyncContainer,
    register_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    login_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, str], Awaitable[PersistableEntity]
    ],
) -> None:
    session_service = await async_container.get(ISessionService)
    email = "employee@example.com"

    refresh_before = await register_subject(Employee, email=email)
    refresh_fingerprint_before = session_service.get_refresh_token_fingerprint(
        refresh_before.refresh_token.get_secret_value()
    )
    auth_session_before: AuthSession = cast(
        AuthSession,
        await uow_get_one_single_model(
            AuthSession, "refresh_token_fingerprint", refresh_fingerprint_before
        ),
    )
    auth_session_snapshot_before = to_dto(auth_session_before)

    refresh_new = await login_subject(Employee, email=email)
    refresh_fingerprint_after = session_service.get_refresh_token_fingerprint(
        refresh_new.refresh_token.get_secret_value()
    )
    auth_session_after: AuthSession = cast(
        AuthSession,
        await uow_get_one_single_model(
            AuthSession, "refresh_token_fingerprint", refresh_fingerprint_after
        ),
    )
    auth_session_snapshot_after = to_dto(auth_session_after)

    assert (
        auth_session_snapshot_before.expiration
        <= auth_session_snapshot_after.expiration
    )
    assert (
        auth_session_snapshot_before.account_id
        == auth_session_snapshot_after.account_id
    )


@pytest.mark.asyncio
async def test_auth_manager_login_flow(
    async_container: AsyncContainer,
    register_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    login_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, str], Awaitable[PersistableEntity]
    ],
) -> None:
    session_service = await async_container.get(ISessionService)
    login = "manager"
    password = "password"

    refresh_before = await register_subject(Manager, login=login, password=password)
    refresh_fingerprint_before = session_service.get_refresh_token_fingerprint(
        refresh_before.refresh_token.get_secret_value()
    )
    auth_session_before: AuthSession = cast(
        AuthSession,
        await uow_get_one_single_model(
            AuthSession, "refresh_token_fingerprint", refresh_fingerprint_before
        ),
    )
    auth_session_snapshot_before = to_dto(auth_session_before)

    refresh_new = await login_subject(Manager, login=login, password=password)
    refresh_fingerprint_after = session_service.get_refresh_token_fingerprint(
        refresh_new.refresh_token.get_secret_value()
    )
    auth_session_after: AuthSession = cast(
        AuthSession,
        await uow_get_one_single_model(
            AuthSession, "refresh_token_fingerprint", refresh_fingerprint_after
        ),
    )
    auth_session_snapshot_after = to_dto(auth_session_after)

    assert (
        auth_session_snapshot_before.expiration
        <= auth_session_snapshot_after.expiration
    )
    assert (
        auth_session_snapshot_before.account_id
        == auth_session_snapshot_after.account_id
    )


@pytest.mark.asyncio
async def test_customer_session_refresh(
    async_container: AsyncContainer,
    register_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    login_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, str], Awaitable[PersistableEntity]
    ],
) -> None:
    session_service = await async_container.get(ISessionService)
    authentication_service = await async_container.get(AuthenticationService)
    phone_number = validate_phone_number("+79991234567")

    refresh_before = await register_subject(Customer, phone_number=phone_number)
    refresh_fingerprint_before = session_service.get_refresh_token_fingerprint(
        refresh_before.refresh_token.get_secret_value()
    )
    auth_session_before: AuthSession = cast(
        AuthSession,
        await uow_get_one_single_model(
            AuthSession, "refresh_token_fingerprint", refresh_fingerprint_before
        ),
    )
    auth_session_snapshot_before = to_dto(auth_session_before)

    refresh_new = await authentication_service.refresh_session_customer(
        refresh_fingerprint_before
    )
    refresh_fingerprint_after = session_service.get_refresh_token_fingerprint(
        refresh_new.refresh_token.get_secret_value()
    )
    auth_session_after: AuthSession = cast(
        AuthSession,
        await uow_get_one_single_model(
            AuthSession, "refresh_token_fingerprint", refresh_fingerprint_after
        ),
    )
    auth_session_snapshot_after = to_dto(auth_session_after)

    assert (
        auth_session_snapshot_before.expiration
        <= auth_session_snapshot_after.expiration
    )
    assert (
        auth_session_snapshot_before.account_id
        == auth_session_snapshot_after.account_id
    )


@pytest.mark.asyncio
async def test_customer_get_claim_token(
    async_container: AsyncContainer,
    register_subject: Callable[..., Awaitable[SessionRefreshSchema]],
) -> None:
    session_service = await async_container.get(ISessionService)
    authentication_service = await async_container.get(AuthenticationService)
    phone_number = validate_phone_number("+79991234567")
    refresh = await register_subject(Customer, phone_number=phone_number)
    access = refresh.access_token

    token_payload: AccessTokenPayload | None = session_service.verify_access_token(
        access.get_secret_value()
    )
    assert token_payload
    claim_token = await authentication_service.get_claim_token(token_payload.account_id)
    claim_token2 = await authentication_service.get_claim_token(
        token_payload.account_id
    )

    assert claim_token != claim_token2
