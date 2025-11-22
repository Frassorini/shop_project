from typing import Any, Literal

from plum import dispatch, overload

from shop_project.infrastructure.authentication.exceptions import (
    AuthTypeMismatchException,
)
from shop_project.infrastructure.authentication.helpers.auth_type import AuthType
from shop_project.infrastructure.authentication.helpers.credential import Credential
from shop_project.infrastructure.authentication.helpers.secret import Secret
from shop_project.infrastructure.cryptography.interfaces.secret_hasher import (
    SecretHasher,
)


class SecretService:
    def __init__(self, secret_hasher: SecretHasher) -> None:
        self.secret_hasher = secret_hasher

    def create_secret(self, credential: Credential) -> Secret:
        return self._create_secret(credential.auth_type, credential.payload)

    def verify(self, secret: Secret, credential: Credential) -> bool:
        if secret.auth_type != credential.auth_type:
            raise AuthTypeMismatchException

        return self._verify(secret.auth_type, secret.payload, credential.payload)

    @overload
    def _create_secret(
        self, auth_type: Literal[AuthType.PASSWORD], credential: dict[str, Any]
    ) -> Secret:
        hashed = self.secret_hasher.hash(credential["password"])
        return Secret(auth_type=auth_type, payload=hashed)

    @overload
    def _create_secret(
        self, auth_type: Literal[AuthType.PHONE], credential: dict[str, Any]
    ) -> Secret: ...

    @dispatch
    def _create_secret(
        self, auth_type: AuthType, credential: dict[str, Any]
    ) -> Secret: ...

    @overload
    def _verify(
        self,
        auth_type: Literal[AuthType.PHONE],
        secret: str,
        credential: dict[str, Any],
    ) -> bool:
        print("phone")
        return False

    @overload
    def _verify(
        self,
        auth_type: Literal[AuthType.PASSWORD],
        secret: str,
        credential: dict[str, Any],
    ) -> bool:
        print("password")
        return self.secret_hasher.verify(password=credential["password"], hashed=secret)

    @dispatch
    def _verify(
        self, auth_type: AuthType, secret: str, credential: dict[str, Any]
    ) -> bool: ...
