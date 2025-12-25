from datetime import datetime
from typing import Self
from uuid import UUID

from shop_project.application.shared.base_dto import BaseDTO
from shop_project.infrastructure.entities.claim_token import ClaimToken


class ClaimTokenDTO(BaseDTO[ClaimToken]):
    entity_id: UUID
    token_fingerprint: str
    issued_at: datetime
    expiration: datetime

    @classmethod
    def to_dto(cls, domain_object: ClaimToken) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            token_fingerprint=domain_object.token_fingerprint,
            issued_at=domain_object.issued_at,
            expiration=domain_object.expiration,
        )

    def to_domain(self) -> ClaimToken:
        return ClaimToken.load(
            entity_id=self.entity_id,
            token_fingerprint=self.token_fingerprint,
            issued_at=self.issued_at,
            expiration=self.expiration,
        )
