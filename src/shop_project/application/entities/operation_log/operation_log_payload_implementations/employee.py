from uuid import UUID

from shop_project.application.entities.operation_log.base_operation_log_payload import (
    BaseOperationLogPayload,
)
from shop_project.application.entities.operation_log.operation_code import (
    OperationCodeEnum,
)
from shop_project.domain.interfaces.subject import SubjectEnum


class CreateEmployeeOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.CREATE_EMPLOYEE]
):
    subject_type: SubjectEnum
    subject_id: UUID
    employee_name: str
    employee_id: UUID


class AuthorizeEmployeeOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.AUTHORIZE_EMPLOYEE]
):
    subject_type: SubjectEnum
    subject_id: UUID
    employee_name: str
    employee_id: UUID


class UnauthorizeEmployeeOperationLogPayload(
    BaseOperationLogPayload[OperationCodeEnum.UNAUTHORIZE_EMPLOYEE]
):
    subject_type: SubjectEnum
    subject_id: UUID
    employee_name: str
    employee_id: UUID
