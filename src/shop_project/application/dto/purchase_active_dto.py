from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO


class PurchaseActiveItemDTO(BaseDTO):
    product_id: UUID
    amount: int


class PurchaseActiveDTO(BaseDTO):
    entity_id: UUID
    state: str
    customer_id: UUID
    escrow_account_id: UUID
    items: list[PurchaseActiveItemDTO]
