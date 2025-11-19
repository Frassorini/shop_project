from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO


class PurchaseDraftItemDTO(BaseDTO):
    product_id: UUID
    amount: int


class PurchaseDraftDTO(BaseDTO):
    entity_id: UUID
    state: str
    customer_id: UUID
    items: list[PurchaseDraftItemDTO]
