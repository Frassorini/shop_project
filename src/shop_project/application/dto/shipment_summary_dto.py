from datetime import datetime
from decimal import Decimal
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO


class ShipmentSummaryItemDTO(BaseDTO):
    product_id: UUID
    amount: int


class ShipmentSummaryDTO(BaseDTO):
    entity_id: UUID
    reason: str
    items: list[ShipmentSummaryItemDTO]