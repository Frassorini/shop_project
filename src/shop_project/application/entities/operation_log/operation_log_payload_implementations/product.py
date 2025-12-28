from decimal import Decimal
from uuid import UUID

from shop_project.application.entities.operation_log.base_operation_log_payload import (
    BaseOperationLogPayload,
)
from shop_project.application.entities.operation_log.operation_code import (
    OperationCodeEnum,
)
from shop_project.domain.interfaces.subject import SubjectEnum


class CreateProductOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.CREATE_PRODUCT]
):
    subject_type: SubjectEnum
    subject_id: UUID
    product_id: UUID
    product_name: str
    product_price: Decimal


class UpdateProductOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.UPDATE_PRODUCT]
):
    subject_type: SubjectEnum
    subject_id: UUID
    product_id: UUID
    product_name: str
    product_price: Decimal


class DeleteProductOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.DELETE_PRODUCT]
):
    subject_type: SubjectEnum
    subject_id: UUID
    product_id: UUID
