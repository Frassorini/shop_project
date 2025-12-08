from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, SecretStr

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class ExternalIdTotp(PersistableEntity, BaseModel):
    entity_id: UUID
    external_id_type: str
    external_id: str
    totp_verifier: SecretStr
    issued_at: datetime
    expiration: datetime

    @classmethod
    def load(
        cls,
        entity_id: UUID,
        external_id_type: str,
        external_id: str,
        totp_verifier: SecretStr,
        issued_at: datetime,
        expiration: datetime,
    ) -> Self:
        return cls(
            entity_id=entity_id,
            external_id_type=external_id_type,
            external_id=external_id,
            totp_verifier=totp_verifier,
            issued_at=issued_at,
            expiration=expiration,
        )
