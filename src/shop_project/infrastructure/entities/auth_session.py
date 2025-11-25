from abc import ABC
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class AuthSession(PersistableEntity, BaseModel, ABC):
    entity_id: UUID
    refresh_token: str
    issued_at: datetime
    expires_at: datetime

    def update_refresh_token(self, refresh_token: str) -> None:
        self._refresh_token = refresh_token

    @property
    def refresh_token(self) -> str:
        return self._refresh_token


class CustomerSession(AuthSession): ...


class EmployeeSession(AuthSession): ...


class ManagerSession(AuthSession): ...
