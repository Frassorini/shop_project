from typing import Self
from uuid import UUID

from shop_project.application.shared.base_schema import BaseSchema
from shop_project.application.shared.dto.customer_dto import CustomerDTO


class CustomerSchemaDefault(BaseSchema):
    entity_id: UUID
    name: str

    @classmethod
    def create(cls, dto: CustomerDTO) -> Self:
        return cls.model_validate(dto)
