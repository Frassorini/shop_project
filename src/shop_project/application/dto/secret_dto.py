from uuid import UUID

from pydantic import SecretStr

from shop_project.application.dto.base_dto import BaseDTO


class SecretDTO(BaseDTO):
    entity_id: UUID
    account_id: UUID
    auth_type: str
    payload: SecretStr
