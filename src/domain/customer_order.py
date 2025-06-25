from dataclasses import dataclass
from typing import Any, Self
from enum import Enum
from domain.stock_item import StockItem
from shared.identity_mixin import IdentityMixin
from domain.exceptions import DomainException, StateException
from shared.entity_id import EntityId
from shared.p_snapshotable import PSnapshotable


@dataclass(frozen=True)
class CustomerOrderItem(StockItem, PSnapshotable):
    store_item_id: EntityId
    amount: int
    price: float
    
    def snapshot(self) -> dict[str, Any]:
        return {
            'store_item_id': self.store_item_id.value,
            'amount': self.amount,
            'price': self.price,
        }
    
    @classmethod
    def from_snapshot(cls, snapshot: dict[str, Any]) -> Self:
        return cls(store_item_id=EntityId.from_str(snapshot['store_item_id']), amount=snapshot['amount'], price=snapshot['price'])


class CustomerOrderState(Enum):
    PENDING = 'PENDING'
    RESERVED = 'RESERVED'
    PAID = 'PAID'
    RECEIVED = 'RECEIVED'
    CANCELLED = 'CANCELLED'


class CustomerOrder(IdentityMixin, PSnapshotable):
    def __init__(self, entity_id: EntityId, customer_id: EntityId, store: str) -> None:
        self._entity_id: EntityId = entity_id
        self.customer_id: EntityId = customer_id
        self.store: str = store
        self.state: CustomerOrderState = CustomerOrderState.PENDING
        
        self._items: dict[EntityId, CustomerOrderItem] = {}
    
    @classmethod
    def from_snapshot(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls(EntityId.from_str(snapshot['entity_id']), 
                  EntityId.from_str(snapshot['customer_id']), 
                  snapshot['store'])
        obj.state = CustomerOrderState(snapshot['state'])
        
        items: list[CustomerOrderItem] = [CustomerOrderItem.from_snapshot(item) for item in snapshot['items']]
        obj._items = {item.store_item_id: item for item in items}
        
        return obj
    
    def snapshot(self) -> dict[str, Any]:
        return {'entity_id': self.entity_id.to_str(), 
                'customer_id': self.customer_id.to_str(), 
                'store': self.store, 
                'state': self.state.value, 
                'items': [item.snapshot() for item in self._items.values()],
                }
    
    def _validate_item(self, store_item_id: EntityId, price: float, amount: int, store: str) -> None:
        if store_item_id in self._items:
            raise DomainException('Item already added')
        
        if self.store != store:
            raise DomainException('Item from another store')
        
        if amount <= 0:
            raise DomainException('Amount must be > 0')
        
        if price <= 0:
            raise DomainException('Price must be > 0')
    
    def add_item(self, store_item_id: EntityId, price: float, amount: int, store: str) -> None:
        self._validate_item(store_item_id, price, amount, store)
        
        self._items[store_item_id] = (CustomerOrderItem(
            store_item_id=store_item_id, 
            amount=amount, 
            price=price))
    
    def get_item(self, store_item_id: EntityId) -> CustomerOrderItem:
        return self._items[store_item_id]
        
    def get_items(self) -> list[CustomerOrderItem]:
        return list(self._items.values())    
    
    def _has_state(self, states: list[CustomerOrderState]) -> bool:
        return self.state in states
    
    def _ensure_has_state(self, states: list[CustomerOrderState]) -> None:
        if not self._has_state(states):
            raise StateException('Invalid state')
    
    def can_be_reserved(self) -> bool:
        return self._has_state([CustomerOrderState.PENDING])
    
    def can_be_paid(self) -> bool:
        return self._has_state([CustomerOrderState.RESERVED])
    
    def can_be_received(self) -> bool:
        return self._has_state([CustomerOrderState.PAID])
    
    def can_be_cancelled(self) -> bool:
        return self._has_state([CustomerOrderState.RESERVED, 
                                CustomerOrderState.PAID])
    
    def reserve(self) -> None:
        self._ensure_has_state([CustomerOrderState.PENDING])
        self.state = CustomerOrderState.RESERVED
    
    def pay(self) -> None:
        self._ensure_has_state([CustomerOrderState.RESERVED])
        self.state = CustomerOrderState.PAID
    
    def receive(self) -> None:
        self._ensure_has_state([CustomerOrderState.PAID])
        self.state = CustomerOrderState.RECEIVED
    
    def cancel(self) -> None:
        self._ensure_has_state([CustomerOrderState.RESERVED, 
                                CustomerOrderState.PAID])
        self.state = CustomerOrderState.CANCELLED

