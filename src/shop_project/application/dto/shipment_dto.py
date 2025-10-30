from datetime import datetime
from decimal import Decimal
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO


class ShipmentItemDTO(BaseDTO):
    store_item_id: UUID
    amount: int


class ShipmentDTO(BaseDTO):
    entity_id: UUID
    state: str
    items: list[ShipmentItemDTO]