from abc import ABC
from uuid import UUID

from pydantic import BaseModel, SecretStr

from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.authentication.helpers.auth_type import AuthType


class Secret(PersistableEntity, BaseModel, ABC):
    entity_id: UUID
    account_id: UUID
    auth_type: AuthType
    payload: SecretStr
