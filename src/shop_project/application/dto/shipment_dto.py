from typing import Self
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO, BaseVODTO
from shop_project.domain.entities.shipment import Shipment, ShipmentItem, ShipmentState


class ShipmentItemDTO(BaseVODTO):
    product_id: UUID
    amount: int


class ShipmentDTO(BaseDTO[Shipment]):
    entity_id: UUID
    state: str
    items: list[ShipmentItemDTO]

    @classmethod
    def to_dto(cls, domain_object: Shipment) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            state=domain_object.state.value,
            items=[
                ShipmentItemDTO.model_validate(item) for item in domain_object.items
            ],
        )

    def to_domain(self) -> Shipment:
        return Shipment.load(
            entity_id=self.entity_id,
            state=ShipmentState(self.state),
            items=[ShipmentItem(**item.model_dump()) for item in self.items],
        )
