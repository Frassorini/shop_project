from typing import Literal
from uuid import UUID, uuid4

from plum import dispatch, overload
from pydantic import SecretStr

from shop_project.infrastructure.authentication.exceptions import (
    AuthTypeMismatchException,
)
from shop_project.infrastructure.authentication.helpers.credential import Credential
from shop_project.infrastructure.cryptography.interfaces.secret_hasher import (
    SecretHasher,
)
from shop_project.infrastructure.entities.secret import AuthType, Secret


class SecretService:
    def __init__(self, secret_hasher: SecretHasher) -> None:
        self.secret_hasher = secret_hasher

    def create_secret(self, account_id: UUID, credential: Credential) -> Secret:
        return self._create_secret(account_id, credential.auth_type, credential)

    def verify(self, secret: Secret, credential: Credential) -> bool:
        if secret.auth_type != credential.auth_type:
            raise AuthTypeMismatchException

        return self._verify(secret.auth_type, secret, credential)

    @overload
    def _create_secret(
        self,
        account_id: UUID,
        auth_type: Literal[AuthType.PASSWORD],
        credential: Credential,
    ) -> Secret:
        hashed = self.secret_hasher.hash(
            credential.payload["password"].get_secret_value()
        )
        return Secret(
            entity_id=uuid4(),
            account_id=account_id,
            auth_type=auth_type,
            payload=SecretStr(hashed),
        )

    @overload
    def _create_secret(
        self,
        account_id: UUID,
        auth_type: Literal[AuthType.PHONE],
        credential: Credential,
    ) -> Secret:
        raise NotImplementedError

    @dispatch
    def _create_secret(
        self, account_id: UUID, auth_type: AuthType, credential: Credential
    ) -> Secret: ...

    @overload
    def _verify(
        self,
        auth_type: Literal[AuthType.PHONE],
        secret: Secret,
        credential: Credential,
    ) -> bool:
        return False

    @overload
    def _verify(
        self,
        auth_type: Literal[AuthType.PASSWORD],
        secret: Secret,
        credential: Credential,
    ) -> bool:
        return self.secret_hasher.verify(
            password=credential.payload["password"].get_secret_value(),
            hashed=secret.payload.get_secret_value(),
        )

    @dispatch
    def _verify(
        self, auth_type: AuthType, secret: Secret, credential: Credential
    ) -> bool: ...
