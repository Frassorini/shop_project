from typing import Self
from uuid import UUID

from shop_project.application.entities.task import Task
from shop_project.application.shared.base_dto import BaseDTO


class TaskDTO(BaseDTO[Task]):
    entity_id: UUID
    handler: str
    params_json: str

    @classmethod
    def to_dto(cls, domain_object: Task) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            handler=domain_object.handler,
            params_json=domain_object.params_json,
        )

    def to_domain(self) -> Task:
        return Task.load(
            entity_id=self.entity_id, handler=self.handler, params_json=self.params_json
        )
