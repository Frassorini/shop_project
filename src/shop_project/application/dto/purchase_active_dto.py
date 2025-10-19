from datetime import datetime
from decimal import Decimal
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO


class PurchaseActiveItemDTO(BaseDTO):
    store_item_id: UUID
    amount: int
    price: Decimal

class PurchaseActiveDTO(BaseDTO):
    entity_id: UUID
    state: str
    customer_id: UUID
    store_id: UUID
    items: list[PurchaseActiveItemDTO]