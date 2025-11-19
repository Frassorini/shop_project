from typing import Self
from uuid import UUID

from shop_project.application.dto.customer_dto import CustomerDTO
from shop_project.application.schemas.base_schema import BaseSchema


class CustomerSchemaDefault(BaseSchema):
    entity_id: UUID
    name: str

    @classmethod
    def create(cls, dto: CustomerDTO) -> Self:
        return cls.model_validate(dto)
