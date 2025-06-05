from abc import ABC, abstractmethod
from typing import Protocol

from domain.entity_id import EntityId




class StockItem(Protocol):
    store_item_id: EntityId
    amount: int