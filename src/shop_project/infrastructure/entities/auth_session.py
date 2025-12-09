from abc import ABC
from datetime import datetime
from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class AuthSession(PersistableEntity, BaseModel, ABC):
    entity_id: UUID
    account_id: UUID
    refresh_token_fingerprint: str
    issued_at: datetime
    expiration: datetime

    def update_refresh_token_fingerprint(self, refresh_token_fingerprint: str) -> None:
        self.refresh_token_fingerprint = refresh_token_fingerprint

    @classmethod
    def load(
        cls,
        entity_id: UUID,
        account_id: UUID,
        refresh_token_fingerprint: str,
        issued_at: datetime,
        expiration: datetime,
        **kw: Any,
    ) -> Self:
        obj = cls(
            entity_id=entity_id,
            account_id=account_id,
            refresh_token_fingerprint=refresh_token_fingerprint,
            issued_at=issued_at,
            expiration=expiration,
        )

        return obj
