from datetime import datetime
from uuid import UUID

from pydantic import SecretStr

from shop_project.application.dto.base_dto import BaseDTO


class ExternalIdTotpDTO(BaseDTO):
    entity_id: UUID
    external_id_type: str
    external_id: str
    totp_verifier: SecretStr
    issued_at: datetime
    expiration: datetime
