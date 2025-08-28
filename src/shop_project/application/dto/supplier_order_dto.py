from datetime import datetime
from decimal import Decimal
from shop_project.application.dto.base_dto import BaseDTO


class SupplierOrderItemDTO(BaseDTO):
    store_item_id: str
    amount: int


class SupplierOrderDTO(BaseDTO):
    entity_id: str
    state: str
    departure: datetime
    arrival: datetime
    store_id: str
    items: list[SupplierOrderItemDTO]