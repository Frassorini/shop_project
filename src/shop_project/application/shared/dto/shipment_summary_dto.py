from typing import Self
from uuid import UUID

from shop_project.application.shared.base_dto import BaseDTO, BaseVODTO
from shop_project.domain.entities.shipment_summary import (
    ShipmentSummary,
    ShipmentSummaryItem,
    ShipmentSummaryReason,
)


class ShipmentSummaryItemDTO(BaseVODTO):
    product_id: UUID
    amount: int


class ShipmentSummaryDTO(BaseDTO[ShipmentSummary]):
    entity_id: UUID
    reason: str
    items: list[ShipmentSummaryItemDTO]

    @classmethod
    def to_dto(cls, domain_object: ShipmentSummary) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            reason=domain_object.reason.value,
            items=[
                ShipmentSummaryItemDTO.model_validate(item)
                for item in domain_object.items
            ],
        )

    def to_domain(self) -> ShipmentSummary:
        return ShipmentSummary.load(
            entity_id=self.entity_id,
            reason=ShipmentSummaryReason(self.reason),
            items=[ShipmentSummaryItem(**item.model_dump()) for item in self.items],
        )
