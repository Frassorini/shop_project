from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO


class CustomerDTO(BaseDTO):
    entity_id: UUID
    name: str
