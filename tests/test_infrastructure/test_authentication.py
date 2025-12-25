from typing import Callable
from uuid import uuid4

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.shared.interfaces.interface_claim_token_service import (
    IClaimTokenService,
)
from shop_project.domain.entities.customer import Customer
from shop_project.domain.interfaces.subject import (
    Subject,
)
from shop_project.infrastructure.authentication.helpers.access_token_payload import (
    AccessTokenPayload,
)
from shop_project.infrastructure.authentication.services.session_service import (
    SessionRefresh,
    SessionService,
)
from shop_project.infrastructure.entities.account import Account, SubjectEnum
from shop_project.infrastructure.entities.auth_session import AuthSession
from shop_project.infrastructure.entities.claim_token import ClaimToken
from tests.fixtures.infrastructure.account import AccountService


@pytest.mark.asyncio
async def test_account(customer_account: Callable[[], Account]):
    account = customer_account()

    assert isinstance(account, Account)


@pytest.mark.asyncio
async def test_password(
    customer_account: Callable[[], Account], async_container: AsyncContainer
):
    secret_service = await async_container.get(AccountService)

    account = customer_account()
    secret_service.set_password(account, "password")

    assert secret_service.verify_password(account, "password")
    assert not secret_service.verify_password(account, "wrong_password")


@pytest.mark.asyncio
async def test_create_session(
    async_container: AsyncContainer,
    customer_andrew: Callable[[], Customer],
    subject_account: Callable[[Subject], Account],
):
    session_service = await async_container.get(SessionService)

    customer = customer_andrew()
    account = subject_account(customer)
    session, sesion_refresh = session_service.create_session(account, customer)

    assert isinstance(session, AuthSession)
    assert isinstance(sesion_refresh, SessionRefresh)

    assert session.account_id == account.entity_id


@pytest.mark.asyncio
async def test_verify_session(
    async_container: AsyncContainer,
    customer_andrew: Callable[[], Customer],
    subject_account: Callable[[Subject], Account],
):
    session_service = await async_container.get(SessionService)

    customer = customer_andrew()
    account = subject_account(customer)
    session, sesion_refresh = session_service.create_session(account, customer)

    assert session_service.verify_session(
        session, sesion_refresh.refresh_token.get_secret_value()
    )
    assert not session_service.verify_session(session, uuid4().hex)


@pytest.mark.asyncio
async def test_access_token(
    async_container: AsyncContainer,
    customer_andrew: Callable[[], Customer],
    subject_account: Callable[[Subject], Account],
):
    session_service = await async_container.get(SessionService)
    customer = customer_andrew()
    account = subject_account(customer)
    session, sesion_refresh = session_service.create_session(account, customer)

    token_payload: AccessTokenPayload | None = session_service.verify_access_token(
        sesion_refresh.access_token.get_secret_value()
    )

    assert token_payload
    assert token_payload.subject_type == SubjectEnum.CUSTOMER
    assert token_payload.account_id == account.entity_id

    assert not session_service.verify_access_token(uuid4().hex)


@pytest.mark.asyncio
async def test_claim_token(
    async_container: AsyncContainer,
    customer_andrew: Callable[[], Customer],
):
    session_service = await async_container.get(IClaimTokenService)
    customer = customer_andrew()

    claim_token, raw_token = session_service.create(customer.entity_id)

    assert isinstance(claim_token, ClaimToken)
    assert isinstance(raw_token, str)

    assert session_service.verify(claim_token, raw_token)
