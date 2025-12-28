from shop_project.application.entities.operation_log.operation_log import OperationLog
from shop_project.application.shared.dto.operation_log_dto import OperationLogDTO
from shop_project.infrastructure.persistence.database.models.operation_log import (
    OperationLog as OperationLogORM,
)
from shop_project.infrastructure.persistence.repositories.base_repository import (
    BaseRepository,
)


class OperationLogRepository(
    BaseRepository[OperationLogORM, OperationLogDTO, OperationLog]
):
    pass
