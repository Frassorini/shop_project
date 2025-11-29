from abc import ABC
from datetime import datetime
from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class AuthSession(PersistableEntity, BaseModel, ABC):
    entity_id: UUID
    account_id: UUID
    refresh_token: str
    issued_at: datetime
    expires_at: datetime

    def update_refresh_token_hash(self, refresh_token_hash: str) -> None:
        self._refresh_token = refresh_token_hash

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    @classmethod
    def _load(
        cls,
        entity_id: UUID,
        account_id: UUID,
        refresh_token: str,
        issued_at: datetime,
        expires_at: datetime,
        **kw: Any,
    ) -> Self:
        obj = cls(
            entity_id=entity_id,
            account_id=account_id,
            refresh_token=refresh_token,
            issued_at=issued_at,
            expires_at=expires_at,
        )

        return obj
