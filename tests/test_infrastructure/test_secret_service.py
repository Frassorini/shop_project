from typing import Literal

import pytest

from shop_project.infrastructure.authentication.exceptions import (
    AuthTypeMismatchException,
)
from shop_project.infrastructure.authentication.helpers.auth_type import AuthType
from shop_project.infrastructure.authentication.helpers.credential import Credential
from shop_project.infrastructure.authentication.helpers.secret import Secret
from shop_project.infrastructure.authentication.services.secret_service import (
    SecretService,
)
from shop_project.infrastructure.cryptography.bcrypt_hasher import BcryptPasswordHasher


def test_auth_type():
    auth: Literal[AuthType.PASSWORD] = AuthType.PASSWORD

    assert auth == AuthType.PASSWORD


def test_secret_service():
    secret_service = SecretService(BcryptPasswordHasher())

    secret = secret_service.create_secret(
        credential=Credential(
            auth_type=AuthType.PASSWORD, payload={"password": "password"}
        )
    )

    assert secret_service.verify(
        secret=secret,
        credential=Credential(
            auth_type=AuthType.PASSWORD, payload={"password": "password"}
        ),
    )


def test_auth_type_mismatch():
    with pytest.raises(AuthTypeMismatchException):
        SecretService(BcryptPasswordHasher()).verify(
            Secret(auth_type=AuthType.PASSWORD, payload="password"),
            Credential(auth_type=AuthType.PHONE, payload={"password": "password"}),
        )
