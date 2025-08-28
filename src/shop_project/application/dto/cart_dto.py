from datetime import datetime
from decimal import Decimal
from shop_project.application.dto.base_dto import BaseDTO


class CartItemDTO(BaseDTO):
    store_item_id: str
    amount: int


class CartDTO(BaseDTO):
    entity_id: str
    customer_id: str
    store_id: str
    items: list[CartItemDTO]