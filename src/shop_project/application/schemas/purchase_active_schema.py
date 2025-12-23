from decimal import Decimal
from typing import Self
from uuid import UUID

from shop_project.application.dto.escrow_account_dto import EscrowAccountDTO
from shop_project.application.dto.purchase_active_dto import PurchaseActiveDTO
from shop_project.application.schemas.base_schema import BaseSchema


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
        purchase_active_dto: PurchaseActiveDTO,
        escrow_account_dto: EscrowAccountDTO,
    ) -> Self:
        return cls(
            entity_id=purchase_active_dto.entity_id,
            payment_state=escrow_account_dto.state,
            price=escrow_account_dto.total_amount,
            customer_id=purchase_active_dto.customer_id,
            items=[
                PurchaseActiveItemSchema.model_validate(item)
                for item in purchase_active_dto.items
            ],
        )


class PurchaseActivationSchema(BaseSchema):
    purchase_active: PurchaseActiveSchema
    payment_url: str
