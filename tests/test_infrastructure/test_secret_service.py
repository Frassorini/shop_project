from typing import Literal
from uuid import uuid4

import pytest
from dishka.async_container import AsyncContainer
from pydantic import SecretStr

from shop_project.infrastructure.authentication.exceptions import (
    AuthTypeMismatchException,
)
from shop_project.infrastructure.authentication.helpers.auth_type import AuthType
from shop_project.infrastructure.authentication.helpers.credential import Credential
from shop_project.infrastructure.authentication.services.secret_service import (
    SecretService,
)


def test_auth_type():
    auth: Literal[AuthType.PASSWORD] = AuthType.PASSWORD

    assert auth == AuthType.PASSWORD


@pytest.mark.asyncio
async def test_secret_service(async_container: AsyncContainer):
    secret_service = await async_container.get(SecretService)

    secret = secret_service.create_secret(
        account_id=uuid4(),
        credential=Credential(
            auth_type=AuthType.PASSWORD, payload={"password": SecretStr("password")}
        ),
    )

    assert secret_service.verify(
        secret=secret,
        credential=Credential(
            auth_type=AuthType.PASSWORD, payload={"password": SecretStr("password")}
        ),
    )


@pytest.mark.asyncio
async def test_auth_type_mismatch(async_container: AsyncContainer):
    secret_service = await async_container.get(SecretService)
    secret = secret_service.create_secret(
        account_id=uuid4(),
        credential=Credential(
            auth_type=AuthType.PASSWORD, payload={"password": SecretStr("password")}
        ),
    )
    with pytest.raises(AuthTypeMismatchException):
        secret_service.verify(
            secret=secret,
            credential=Credential(
                auth_type=AuthType.PHONE, payload={"password": SecretStr("password")}
            ),
        )
