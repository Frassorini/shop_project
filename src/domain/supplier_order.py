from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Self

from domain.entity_id import EntityId
from domain.entity_mixin import EntityMixin
from domain.exceptions import DomainException, StateException
from domain.stock_item import StockItem


class SupplierOrderState(Enum):
    PENDING = 'PENDING'
    DEPARTED = 'DEPARTED'
    RECEIVED = 'RECEIVED'
    CANCELLED = 'CANCELLED'


@dataclass(frozen=True)
class SupplierOrderItem(StockItem):
    store_item_id: EntityId
    amount: int

class SupplierOrder(EntityMixin):
    def __init__(self, entity_id: EntityId, departure: datetime, arrival: datetime, store: str) -> None:
        super().__init__()
        self._entity_id: EntityId = entity_id
        self.departure: datetime = departure
        self.arrival: datetime = arrival
        self.store: str = store
        self.state: SupplierOrderState = SupplierOrderState.PENDING
        
        self._items: dict[EntityId, SupplierOrderItem] = {}
        
    def _validate_item(self, store_item_id: EntityId, amount: int, store: str) -> None:
        if store_item_id in self._items:
            raise DomainException('Item already added')
        
        if self.store != store:
            raise DomainException('Item from another store')
        
        if amount <= 0:
            raise DomainException('Amount must be > 0')
    
    def add_item(self, store_item_id: EntityId, amount: int, store: str) -> None:
        self._validate_item(store_item_id, amount, store)
        
        self._items[store_item_id] = (SupplierOrderItem(
            store_item_id=store_item_id, 
            amount=amount))
    
    def get_item(self, store_item_id: EntityId) -> SupplierOrderItem:
        return self._items[store_item_id]
        
    def get_items(self) -> list[SupplierOrderItem]:
        return list(self._items.values())    
    
    def _has_state(self, states: list[SupplierOrderState]) -> bool:
        return self.state in states
    
    def _ensure_has_state(self, states: list[SupplierOrderState]) -> None:
        if not self._has_state(states):
            raise StateException('Invalid state')
    
    def can_be_departed(self) -> bool:
        return self._has_state([SupplierOrderState.PENDING])
    
    def can_be_received(self) -> bool:
        return self._has_state([SupplierOrderState.DEPARTED])
    
    def can_be_cancelled(self) -> bool:
        return self._has_state([SupplierOrderState.DEPARTED])
    
    def depart(self) -> None:
        self._ensure_has_state([SupplierOrderState.PENDING])
        self.state = SupplierOrderState.DEPARTED
    
    def receive(self) -> None:
        self._ensure_has_state([SupplierOrderState.DEPARTED])
        self.state = SupplierOrderState.RECEIVED
    
    def cancel(self) -> None:
        self._ensure_has_state([SupplierOrderState.DEPARTED])
        self.state = SupplierOrderState.CANCELLED