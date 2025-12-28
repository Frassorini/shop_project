from uuid import UUID

from pydantic import BaseModel

from shop_project.application.entities.operation_log.base_operation_log_payload import (
    BaseOperationLogPayload,
)
from shop_project.application.entities.operation_log.operation_code import (
    OperationCodeEnum,
)
from shop_project.domain.interfaces.subject import SubjectEnum


class ActivateShipmentItem(BaseModel):
    product_id: UUID
    amount: int


class ActivateShipmentOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.ACTIVATE_SHIPMENT]
):
    subject_type: SubjectEnum
    subject_id: UUID
    shipment_id: UUID
    items: list[ActivateShipmentItem]


class CancelShipmentOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.CANCEL_SHIPMENT]
):
    subject_type: SubjectEnum
    subject_id: UUID
    shipment_id: UUID


class ReceiveShipmentOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.RECEIVE_SHIPMENT]
):
    subject_type: SubjectEnum
    subject_id: UUID
    shipment_id: UUID
