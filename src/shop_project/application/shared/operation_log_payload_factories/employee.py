from shop_project.application.entities.operation_log.operation_log_payload_implementations.employee import (
    AuthorizeEmployeeOperationLogPayload,
    CreateEmployeeOperationLogPayload,
    UnauthorizeEmployeeOperationLogPayload,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.dto.employee_dto import EmployeeDTO


def create_create_employee_payload(
    access_token_payload: AccessTokenPayload, employee_dto: EmployeeDTO
) -> CreateEmployeeOperationLogPayload:
    return CreateEmployeeOperationLogPayload(
        subject_type=access_token_payload.subject_type,
        subject_id=access_token_payload.account_id,
        employee_name=employee_dto.name,
        employee_id=employee_dto.entity_id,
    )


def create_authorize_employee_payload(
    access_token_payload: AccessTokenPayload, employee_dto: EmployeeDTO
) -> AuthorizeEmployeeOperationLogPayload:
    return AuthorizeEmployeeOperationLogPayload(
        subject_type=access_token_payload.subject_type,
        subject_id=access_token_payload.account_id,
        employee_name=employee_dto.name,
        employee_id=employee_dto.entity_id,
    )


def create_unauthorize_employee_payload(
    access_token_payload: AccessTokenPayload, employee_dto: EmployeeDTO
) -> UnauthorizeEmployeeOperationLogPayload:
    return UnauthorizeEmployeeOperationLogPayload(
        subject_type=access_token_payload.subject_type,
        subject_id=access_token_payload.account_id,
        employee_name=employee_dto.name,
        employee_id=employee_dto.entity_id,
    )
