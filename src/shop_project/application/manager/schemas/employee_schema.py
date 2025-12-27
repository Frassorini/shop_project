from uuid import UUID

from shop_project.application.shared.base_schema import BaseSchema


class EmployeeSchema(BaseSchema):
    entity_id: UUID
    name: str
