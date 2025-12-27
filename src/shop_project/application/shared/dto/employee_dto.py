from typing import Self
from uuid import UUID

from shop_project.application.shared.base_dto import BaseDTO
from shop_project.domain.entities.employee import Employee, EmployeeState


class EmployeeDTO(BaseDTO[Employee]):
    entity_id: UUID
    name: str
    state: str

    @classmethod
    def to_dto(cls, domain_object: Employee) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            name=domain_object.name,
            state=domain_object.state.value,
        )

    def to_domain(self) -> Employee:
        return Employee.load(
            entity_id=self.entity_id,
            name=self.name,
            state=EmployeeState[self.state],
        )
