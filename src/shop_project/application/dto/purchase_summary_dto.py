from typing import Self
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO, BaseVODTO
from shop_project.domain.entities.purchase_summary import (
    PurchaseSummary,
    PurchaseSummaryItem,
    PurchaseSummaryReason,
)


class PurchaseSummaryItemDTO(BaseVODTO):
    product_id: UUID
    amount: int


class PurchaseSummaryDTO(BaseDTO[PurchaseSummary]):
    entity_id: UUID
    reason: str
    customer_id: UUID
    escrow_account_id: UUID
    items: list[PurchaseSummaryItemDTO]

    @classmethod
    def to_dto(cls, domain_object: PurchaseSummary) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            customer_id=domain_object.customer_id,
            escrow_account_id=domain_object.escrow_account_id,
            reason=domain_object.reason.value,
            items=[
                PurchaseSummaryItemDTO.model_validate(item)
                for item in domain_object.items
            ],
        )

    def to_domain(self) -> PurchaseSummary:
        return PurchaseSummary.load(
            entity_id=self.entity_id,
            customer_id=self.customer_id,
            escrow_account_id=self.escrow_account_id,
            reason=PurchaseSummaryReason(self.reason),
            items=[PurchaseSummaryItem(**item.model_dump()) for item in self.items],
        )
