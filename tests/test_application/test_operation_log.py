from uuid import uuid4

from shop_project.application.entities.operation_log.operation_code import (
    OperationCodeEnum,
)
from shop_project.application.entities.operation_log.operation_log import (
    create_operation_log,
)
from shop_project.application.entities.operation_log.operation_log_payload_implementations.employee import (
    CreateEmployeeOperationLogPayload,
)
from shop_project.domain.interfaces.subject import SubjectEnum


def test_create_operation_log():
    payload = CreateEmployeeOperationLogPayload(
        subject_type=SubjectEnum.MANAGER,
        subject_id=uuid4(),
        employee_name="John Doe",
        employee_id=uuid4(),
    )
    operation_log = create_operation_log(payload=payload)
    assert operation_log.operation_code == OperationCodeEnum.CREATE_EMPLOYEE.value
