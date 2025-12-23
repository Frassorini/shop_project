from datetime import datetime
from typing import Any, Self
from uuid import UUID

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class ClaimToken(PersistableEntity):
    def __init__(
        self,
        entity_id: UUID,
        token_fingerprint: str,
        issued_at: datetime,
        expiration: datetime,
    ) -> None:
        self.entity_id: UUID = entity_id
        self.token_fingerprint: str = token_fingerprint
        self.issued_at: datetime = issued_at
        self.expiration: datetime = expiration

    def update_token_fingerprint(self, token_fingerprint: str) -> None:
        self.token_fingerprint = token_fingerprint

    @classmethod
    def load(
        cls,
        entity_id: UUID,
        token_fingerprint: str,
        issued_at: datetime,
        expiration: datetime,
        **kw: Any,
    ) -> Self:
        obj = cls(
            entity_id=entity_id,
            token_fingerprint=token_fingerprint,
            issued_at=issued_at,
            expiration=expiration,
        )

        return obj
