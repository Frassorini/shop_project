from datetime import datetime
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO


class AuthSessionDTO(BaseDTO):
    entity_id: UUID
    account_id: UUID
    refresh_token: str
    issued_at: datetime
    expires_at: datetime
