from typing import Self
from uuid import UUID

from shop_project.application.shared.base_dto import BaseDTO
from shop_project.domain.entities.manager import Manager


class ManagerDTO(BaseDTO[Manager]):
    entity_id: UUID
    name: str

    @classmethod
    def to_dto(cls, domain_object: Manager) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            name=domain_object.name,
        )

    def to_domain(self) -> Manager:
        return Manager.load(
            entity_id=self.entity_id,
            name=self.name,
        )
