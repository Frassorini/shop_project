from shop_project.application.entities.operation_log.operation_log_payload_implementations.background import (
    ManualRedeliverTasksOperationLogPayload,
    ManualTriggerPurchaseFlowOperationLogPayload,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload


def create_manual_trigger_purchase_flow_payload(
    access_token_payload: AccessTokenPayload,
) -> ManualTriggerPurchaseFlowOperationLogPayload:
    return ManualTriggerPurchaseFlowOperationLogPayload(
        subject_type=access_token_payload.subject_type,
        subject_id=access_token_payload.account_id,
    )


def create_manual_redeliver_tasks_payload(
    access_token_payload: AccessTokenPayload,
) -> ManualRedeliverTasksOperationLogPayload:
    return ManualRedeliverTasksOperationLogPayload(
        subject_type=access_token_payload.subject_type,
        subject_id=access_token_payload.account_id,
    )
