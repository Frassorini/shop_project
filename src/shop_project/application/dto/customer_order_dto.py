from datetime import datetime
from decimal import Decimal
from shop_project.application.dto.base_dto import BaseDTO


class CustomerOrderItemDTO(BaseDTO):
    store_item_id: str
    amount: int
    price: Decimal

class CustomerOrderDTO(BaseDTO):
    entity_id: str
    state: str
    customer_id: str
    store_id: str
    items: list[CustomerOrderItemDTO]