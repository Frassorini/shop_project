from decimal import Decimal
from typing import Self
from uuid import UUID

from shop_project.application.shared.base_schema import BaseSchema
from shop_project.application.shared.dto.escrow_account_dto import EscrowAccountDTO
from shop_project.application.shared.dto.purchase_active_dto import PurchaseActiveDTO


class PurchaseActiveItemSchema(BaseSchema):
    product_id: UUID
    amount: int


class PurchaseActiveSchema(BaseSchema):
    entity_id: UUID
    payment_state: str
    price: Decimal
    customer_id: UUID
    items: list[PurchaseActiveItemSchema]

    @classmethod
    def create(
        cls,
        purchase_summary_dto: PurchaseActiveDTO,
        escrow_account_dto: EscrowAccountDTO,
    ) -> Self:
        return cls(
            entity_id=purchase_summary_dto.entity_id,
            payment_state=escrow_account_dto.state,
            price=escrow_account_dto.total_amount,
            customer_id=purchase_summary_dto.customer_id,
            items=[
                PurchaseActiveItemSchema.model_validate(item)
                for item in purchase_summary_dto.items
            ],
        )


class PurchaseActivationSchema(BaseSchema):
    purchase_active: PurchaseActiveSchema
    payment_url: str
