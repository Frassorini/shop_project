from shop_project.application.dto.employee_dto import EmployeeDTO
from shop_project.domain.entities.employee import Employee
from shop_project.infrastructure.persistence.database.models.employee import (
    Employee as EmployeeORM,
)
from shop_project.infrastructure.persistence.repositories.base_repository import (
    BaseRepository,
)


class EmployeeRepository(BaseRepository[EmployeeORM, EmployeeDTO, Employee]):
    pass
