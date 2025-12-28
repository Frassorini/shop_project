from datetime import datetime
from typing import Self
from uuid import UUID

from shop_project.application.entities.operation_log.operation_log import OperationLog
from shop_project.application.shared.base_dto import BaseDTO


class OperationLogDTO(BaseDTO[OperationLog]):
    entity_id: UUID
    operation_code: str
    payload_json: str
    occured_at: datetime
    seq: int | None

    @classmethod
    def to_dto(cls, domain_object: OperationLog) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            operation_code=domain_object.operation_code,
            payload_json=domain_object.payload_json,
            occured_at=domain_object.occured_at,
            seq=domain_object.seq,
        )

    def to_domain(self) -> OperationLog:
        return OperationLog.load(
            entity_id=self.entity_id,
            operation_code=self.operation_code,
            payload_json=self.payload_json,
            occured_at=self.occured_at,
            seq=self.seq,
        )
