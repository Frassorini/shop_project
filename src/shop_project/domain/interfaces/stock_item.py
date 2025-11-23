from typing import Protocol
from uuid import UUID


class StockItem(Protocol):
    product_id: UUID
    amount: int
