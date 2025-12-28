from datetime import datetime, timezone
from typing import Any, Self
from uuid import UUID, uuid4

from shop_project.application.entities.operation_log.base_operation_log_payload import (
    BaseOperationLogPayload,
)
from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class OperationLog(PersistableEntity):
    def __init__(
        self,
        entity_id: UUID,
        operation_code: str,
        payload_json: str,
        occured_at: datetime,
    ) -> None:
        self.entity_id: UUID = entity_id
        self.operation_code: str = operation_code
        self.payload_json: str = payload_json
        self.occured_at: datetime = occured_at
        self.seq: int | None = None

    @classmethod
    def load(
        cls,
        entity_id: UUID,
        operation_code: str,
        payload_json: str,
        occured_at: datetime,
        seq: int | None,
    ) -> Self:
        obj = cls(
            entity_id=entity_id,
            operation_code=operation_code,
            payload_json=payload_json,
            occured_at=occured_at,
        )

        obj.seq = seq

        return obj


def create_operation_log(
    payload: BaseOperationLogPayload[Any],
) -> OperationLog:
    return OperationLog(
        entity_id=uuid4(),
        operation_code=payload.get_operation_code().value,
        payload_json=payload.get_payload_json(),
        occured_at=datetime.now(tz=timezone.utc),
    )
