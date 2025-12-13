from typing import Self
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO, BaseVODTO
from shop_project.domain.entities.purchase_draft import (
    PurchaseDraft,
    PurchaseDraftItem,
    PurchaseDraftState,
)


class PurchaseDraftItemDTO(BaseVODTO):
    product_id: UUID
    amount: int


class PurchaseDraftDTO(BaseDTO[PurchaseDraft]):
    entity_id: UUID
    state: str
    customer_id: UUID
    items: list[PurchaseDraftItemDTO]

    @classmethod
    def to_dto(cls, domain_object: PurchaseDraft) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            state=domain_object.state.value,
            customer_id=domain_object.customer_id,
            items=[
                PurchaseDraftItemDTO.model_validate(item)
                for item in domain_object.items
            ],
        )

    def to_domain(self) -> PurchaseDraft:
        return PurchaseDraft.load(
            entity_id=self.entity_id,
            state=PurchaseDraftState(self.state),
            customer_id=self.customer_id,
            items=[PurchaseDraftItem(**item.model_dump()) for item in self.items],
        )
