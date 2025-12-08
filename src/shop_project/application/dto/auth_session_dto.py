from datetime import datetime
from uuid import UUID

from pydantic import SecretStr

from shop_project.application.dto.base_dto import BaseDTO


class AuthSessionDTO(BaseDTO):
    entity_id: UUID
    account_id: UUID
    refresh_token_fingerprint: SecretStr
    issued_at: datetime
    expiration: datetime
