from typing import Protocol
from uuid import UUID

from shop_project.infrastructure.authentication.helpers.credential import Credential
from shop_project.infrastructure.entities.secret import Secret


class ISecretService(Protocol):
    def create_secret(self, account_id: UUID, credential: Credential) -> Secret: ...

    def verify(self, secret: Secret, credential: Credential) -> bool: ...
