from typing import Any

from shop_project.application.entities.operation_log.base_operation_log_payload import (
    BaseOperationLogPayload,
)
from shop_project.application.entities.operation_log.operation_log import (
    OperationLog,
    create_operation_log,
)
from shop_project.application.shared.interfaces.interface_resource_container import (
    IResourceContainer,
)


def log_operation(
    resources: IResourceContainer,
    payload: BaseOperationLogPayload[Any],
) -> None:
    operation_log = create_operation_log(payload)
    resources.put(OperationLog, operation_log)
