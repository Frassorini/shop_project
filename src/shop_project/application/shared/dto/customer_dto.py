from typing import Self
from uuid import UUID

from shop_project.application.shared.base_dto import BaseDTO
from shop_project.domain.entities.customer import Customer


class CustomerDTO(BaseDTO[Customer]):
    entity_id: UUID
    name: str

    @classmethod
    def to_dto(cls, domain_object: Customer) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            name=domain_object.name,
        )

    def to_domain(self) -> Customer:
        return Customer.load(
            entity_id=self.entity_id,
            name=self.name,
        )
