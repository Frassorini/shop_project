from datetime import datetime
from decimal import Decimal
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO


class PurchaseSummaryItemDTO(BaseDTO):
    store_item_id: UUID
    amount: int


class PurchaseSummaryDTO(BaseDTO):
    entity_id: UUID
    reason: str
    customer_id: UUID
    escrow_account_id: UUID
    items: list[PurchaseSummaryItemDTO]