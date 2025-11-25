from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO


class AccountDTO(BaseDTO):
    entity_id: UUID
    subject_type: str
