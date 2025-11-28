from typing import Callable, Literal
from uuid import uuid4

import pytest
from dishka.async_container import AsyncContainer

from shop_project.domain.entities.customer import Customer
from shop_project.infrastructure.authentication.helpers.access_token_payload import (
    AccessTokenPayload,
)
from shop_project.infrastructure.authentication.helpers.auth_type import AuthType
from shop_project.infrastructure.authentication.helpers.subject_type_union import (
    SubjectTypeUnion,
)
from shop_project.infrastructure.authentication.services.session_service import (
    SessionRefresh,
    SessionService,
)
from shop_project.infrastructure.entities.account import Account, SubjectType
from shop_project.infrastructure.entities.auth_session import AuthSession


def test_auth_type():
    auth: Literal[AuthType.PASSWORD] = AuthType.PASSWORD

    assert auth == AuthType.PASSWORD


@pytest.mark.asyncio
async def test_account(customer_account: Callable[[], Account]):
    account = customer_account()

    assert isinstance(account, Account)


@pytest.mark.asyncio
async def test_create_session(
    async_container: AsyncContainer,
    customer_andrew: Callable[[], Customer],
    subject_account: Callable[[SubjectTypeUnion], Account],
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
    subject_account: Callable[[SubjectTypeUnion], Account],
):
    session_service = await async_container.get(SessionService)

    customer = customer_andrew()
    account = subject_account(customer)
    session, sesion_refresh = session_service.create_session(account, customer)

    assert session_service.verify_session(session, sesion_refresh.refresh_token)
    assert not session_service.verify_session(session, uuid4().hex)


@pytest.mark.asyncio
async def test_access_token(
    async_container: AsyncContainer,
    customer_andrew: Callable[[], Customer],
    subject_account: Callable[[SubjectTypeUnion], Account],
):
    session_service = await async_container.get(SessionService)
    customer = customer_andrew()
    account = subject_account(customer)
    session, sesion_refresh = session_service.create_session(account, customer)

    token_payload: AccessTokenPayload | None = session_service.verify_access_token(
        sesion_refresh.access_token
    )

    assert token_payload
    assert token_payload.subject_type == SubjectType.CUSTOMER
    assert token_payload.account_id == account.entity_id

    assert not session_service.verify_access_token(uuid4().hex)
