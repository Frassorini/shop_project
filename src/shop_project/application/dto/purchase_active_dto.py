from typing import Self
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO, BaseVODTO
from shop_project.domain.entities.purchase_active import (
    PurchaseActive,
    PurchaseActiveItem,
    PurchaseActiveState,
)


class PurchaseActiveItemDTO(BaseVODTO):
    product_id: UUID
    amount: int


class PurchaseActiveDTO(BaseDTO[PurchaseActive]):
    entity_id: UUID
    state: str
    customer_id: UUID
    escrow_account_id: UUID
    items: list[PurchaseActiveItemDTO]

    @classmethod
    def to_dto(cls, domain_object: PurchaseActive) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            state=domain_object.state.value,
            customer_id=domain_object.customer_id,
            escrow_account_id=domain_object.escrow_account_id,
            items=[
                PurchaseActiveItemDTO.model_validate(item)
                for item in domain_object.items
            ],
        )

    def to_domain(self) -> PurchaseActive:
        return PurchaseActive.load(
            entity_id=self.entity_id,
            state=PurchaseActiveState(self.state),
            customer_id=self.customer_id,
            escrow_account_id=self.escrow_account_id,
            items=[PurchaseActiveItem(**item.model_dump()) for item in self.items],
        )
