from datetime import datetime
from decimal import Decimal
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO


class CartItemDTO(BaseDTO):
    store_item_id: UUID
    amount: int


class CartDTO(BaseDTO):
    entity_id: UUID
    customer_id: UUID
    store_id: UUID
    items: list[CartItemDTO]