from abc import ABC
from datetime import datetime, timedelta, timezone
from typing import Any, Self
from uuid import UUID

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class AuthSession(PersistableEntity, ABC):
    def __init__(self, subject_id: UUID, ttl: timedelta, refresh_token: str) -> None:
        self.entity_id: UUID = subject_id  # Привязка к субъекту
        self._refresh_token = refresh_token
        self.issued_at = datetime.now(tz=timezone.utc)
        self.expires_at = self.issued_at + ttl

    def update_refresh_token(self, refresh_token: str) -> None:
        self._refresh_token = refresh_token

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "refresh_token": self.refresh_token,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls.__new__(cls)
        obj.entity_id = snapshot["entity_id"]
        obj._refresh_token = snapshot["refresh_token"]
        obj.issued_at = datetime.fromisoformat(snapshot["issued_at"])
        obj.expires_at = datetime.fromisoformat(snapshot["expires_at"])
        return obj


class CustomerSession(AuthSession): ...


class EmployeeSession(AuthSession): ...


class ManagerSession(AuthSession): ...
