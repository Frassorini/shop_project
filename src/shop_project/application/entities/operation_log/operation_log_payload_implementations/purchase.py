from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from shop_project.application.entities.operation_log.base_operation_log_payload import (
    BaseOperationLogPayload,
)
from shop_project.application.entities.operation_log.operation_code import (
    OperationCodeEnum,
)
from shop_project.domain.interfaces.subject import SubjectEnum


class ActivatePurchaseItem(BaseModel):
    product_id: UUID
    amount: int
    price: Decimal


class ActivatePurchaseOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.ACTIVATE_PURCHASE]
):
    subject_type: SubjectEnum
    subject_id: UUID
    purchase_id: UUID
    items: list[ActivatePurchaseItem]
    total_amount: Decimal


class PayPurchaseOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.PAY_PURCHASE]
):
    purchase_id: UUID
    amount: Decimal
    currency: str
    payment_method: str


class ClaimPurchaseOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.CLAIM_PURCHASE]
):
    subject_type: SubjectEnum
    subject_id: UUID
    subject_type: SubjectEnum
    subject_id: UUID
    purchase_id: UUID


class ManualUnclaimPurchaseOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.MANUAL_UNCLAIM_PURCHASE]
):
    purchase_id: UUID
    reason: str


class AutoUnclaimPurchaseOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.AUTO_UNCLAIM_PURCHASE]
):
    purchase_id: UUID
    reason: str


class RefundPurchaseOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.REFUND_PURCHASE]
):
    purchase_id: UUID
    amount: Decimal


class CancelPurchaseOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.CANCEL_PURCHASE]
):
    purchase_id: UUID
