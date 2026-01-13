from uuid import UUID

from shop_project.application.entities.operation_log.base_operation_log_payload import (
    BaseOperationLogPayload,
)
from shop_project.application.entities.operation_log.operation_code import (
    OperationCodeEnum,
)
from shop_project.domain.interfaces.subject import SubjectEnum


class ManualTriggerPurchaseFlowOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.MANUAL_TRIGGER_PURCHASE_FLOW]
):
    subject_type: SubjectEnum
    subject_id: UUID


class ManualRedeliverTasksOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.MANUAL_REDELIVER_TASKS]
):
    subject_type: SubjectEnum
    subject_id: UUID
