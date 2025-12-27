from datetime import datetime
from typing import Self
from uuid import UUID

from shop_project.application.entities.auth_session import AuthSession
from shop_project.application.shared.base_dto import BaseDTO


class AuthSessionDTO(BaseDTO[AuthSession]):
    entity_id: UUID
    account_id: UUID
    refresh_token_fingerprint: str
    issued_at: datetime
    expiration: datetime

    @classmethod
    def to_dto(cls, domain_object: AuthSession) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            account_id=domain_object.account_id,
            refresh_token_fingerprint=domain_object.refresh_token_fingerprint,
            issued_at=domain_object.issued_at,
            expiration=domain_object.expiration,
        )

    def to_domain(self) -> AuthSession:
        return AuthSession.load(
            entity_id=self.entity_id,
            account_id=self.account_id,
            refresh_token_fingerprint=self.refresh_token_fingerprint,
            issued_at=self.issued_at,
            expiration=self.expiration,
        )
