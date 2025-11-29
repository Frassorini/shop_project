from abc import ABC
from enum import Enum
from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel, SecretStr

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class AuthType(Enum):
    PASSWORD = "PASSWORD"
    PHONE = "PHONE"


class Secret(PersistableEntity, BaseModel, ABC):
    entity_id: UUID
    account_id: UUID
    auth_type: AuthType
    payload: SecretStr

    @classmethod
    def _load(
        cls,
        entity_id: UUID,
        account_id: UUID,
        auth_type: AuthType,
        payload: SecretStr,
        **kw: Any,
    ) -> Self:
        obj = cls(
            entity_id=entity_id,
            account_id=account_id,
            auth_type=auth_type,
            payload=payload,
        )

        return obj
