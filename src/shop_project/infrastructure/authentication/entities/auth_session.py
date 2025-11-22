from abc import ABC
from datetime import datetime, timedelta, timezone
from typing import Any, Self

from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.shared.entity_id import EntityId


class AuthSession(PersistableEntity, ABC):
    def __init__(
        self, subject_id: EntityId, ttl: timedelta, refresh_token: str
    ) -> None:
        self._entity_id: EntityId = subject_id  # Привязка к субъекту
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
            "entity_id": self.entity_id.value,
            "refresh_token": self.refresh_token,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls.__new__(cls)
        obj._entity_id = EntityId(snapshot["entity_id"])
        obj._refresh_token = snapshot["refresh_token"]
        obj.issued_at = datetime.fromisoformat(snapshot["issued_at"])
        obj.expires_at = datetime.fromisoformat(snapshot["expires_at"])
        return obj


class CustomerSession(AuthSession): ...


class EmployeeSession(AuthSession): ...


class ManagerSession(AuthSession): ...
