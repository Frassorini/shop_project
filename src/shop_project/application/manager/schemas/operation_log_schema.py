from datetime import datetime
from uuid import UUID

from shop_project.application.shared.base_schema import BaseSchema


class OperationLogSchema(BaseSchema):
    entity_id: UUID
    operation_code: str
    payload_json: str
    occured_at: datetime
    seq: int | None
