from decimal import Decimal
from typing import Self
from uuid import UUID

from shop_project.application.shared.base_schema import BaseSchema
from shop_project.application.shared.dto.escrow_account_dto import EscrowAccountDTO
from shop_project.application.shared.dto.purchase_summary_dto import PurchaseSummaryDTO


class PurchaseSummaryItemSchema(BaseSchema):
    product_id: UUID
    amount: int


class PurchaseSummarySchema(BaseSchema):
    entity_id: UUID
    reason: str
    customer_id: UUID
    items: list[PurchaseSummaryItemSchema]


class PurchaseSummarySchema(BaseSchema):
    entity_id: UUID
    reason: str
    customer_id: UUID
    payment_state: str
    price: Decimal
    items: list[PurchaseSummaryItemSchema]

    @classmethod
    def create(
        cls,
        purchase_summary_dto: PurchaseSummaryDTO,
        escrow_account_dto: EscrowAccountDTO,
    ) -> Self:
        return cls(
            entity_id=purchase_summary_dto.entity_id,
            reason=purchase_summary_dto.reason,
            customer_id=purchase_summary_dto.customer_id,
            payment_state=escrow_account_dto.state,
            price=escrow_account_dto.total_amount,
            items=[
                PurchaseSummaryItemSchema.model_validate(item)
                for item in purchase_summary_dto.items
            ],
        )
