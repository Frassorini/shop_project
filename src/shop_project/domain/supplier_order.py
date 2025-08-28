from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Mapping, Self, Sequence, cast

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.stock_item import StockItem
from shop_project.shared.entity_id import EntityId
from shop_project.shared.identity_mixin import IdentityMixin
from shop_project.domain.exceptions import DomainException
from shop_project.shared.p_snapshotable import PSnapshotable
from shop_project.shared.base_state_machine import BaseStateMachine


@dataclass(frozen=True)
class SupplierOrderItem(StockItem, PSnapshotable):
    store_item_id: EntityId
    amount: int
    
    def to_dict(self) -> dict[str, Any]:
        return {
            'store_item_id': self.store_item_id.to_str(),
            'amount': self.amount,
        }
    
    
    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        return cls(EntityId(snapshot['store_item_id']), snapshot['amount'])


class SupplierOrderState(Enum):
    PENDING = 'PENDING'
    DEPARTED = 'DEPARTED'
    RECEIVED = 'RECEIVED'
    CANCELLED = 'CANCELLED'


class SupplierOrderStateMachine(BaseStateMachine[SupplierOrderState]):
    _transitions: dict[SupplierOrderState, list[SupplierOrderState]] = {
        SupplierOrderState.PENDING: [SupplierOrderState.DEPARTED],
        SupplierOrderState.DEPARTED: [SupplierOrderState.RECEIVED, SupplierOrderState.CANCELLED],
        SupplierOrderState.RECEIVED: [],
        SupplierOrderState.CANCELLED: [],
    }


class SupplierOrder(BaseAggregate):
    def __init__(self, entity_id: EntityId, departure: datetime, arrival: datetime, store_id: EntityId) -> None:
        self._entity_id: EntityId = entity_id
        self._state_machine: SupplierOrderStateMachine = SupplierOrderStateMachine(SupplierOrderState.PENDING)
        self.departure: datetime = departure
        self.arrival: datetime = arrival
        self.store_id: EntityId = store_id
        
        self._items: dict[EntityId, SupplierOrderItem] = {}
    
    def to_dict(self) -> dict[str, Any]:
        return {'entity_id': self.entity_id.to_str(), 
                'departure': self.departure, 
                'arrival': self.arrival, 
                'store_id': self.store_id.to_str(), 
                'state': self.state.value,
                'items': [item.to_dict() for item in self._items.values()],
                }
    
    # TODO: это ок или не ок???
    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        items_snapshot: list[dict[str, str]] = cast(list[dict[str, str]], snapshot['items'])
        
        obj = cls(EntityId(snapshot['entity_id']),
                  snapshot['departure'], 
                  snapshot['arrival'], 
                  EntityId(snapshot['store_id']),
                  )
        obj._state_machine = SupplierOrderStateMachine(SupplierOrderState(snapshot['state']))
        
        items: list[SupplierOrderItem] = [SupplierOrderItem.from_dict(item) for item in items_snapshot]
        obj._items = {item.store_item_id: item for item in items}
        
        return obj
        
    def _validate_item(self, store_item_id: EntityId, amount: int, store_id: EntityId) -> None:
        if store_item_id in self._items:
            raise DomainException('Item already added')
        
        if self.store_id != store_id:
            raise DomainException('Item from another store')
        
        if amount <= 0:
            raise DomainException('Amount must be > 0')
    
    def add_item(self, store_item_id: EntityId, amount: int, store_id: EntityId) -> None:
        self._validate_item(store_item_id, amount, store_id)
        
        self._items[store_item_id] = (SupplierOrderItem(
            store_item_id=store_item_id, 
            amount=amount))
    
    def get_item(self, store_item_id: EntityId) -> SupplierOrderItem:
        return self._items[store_item_id]
        
    def get_items(self) -> list[SupplierOrderItem]:
        return list(self._items.values())
    
    @property
    def state(self) -> SupplierOrderState:
        return self._state_machine.state    
    
    def can_be_departed(self) -> bool:
        return self._state_machine.can_be_transitioned_to(SupplierOrderState.DEPARTED)
    
    def can_be_received(self) -> bool:
        return self._state_machine.can_be_transitioned_to(SupplierOrderState.RECEIVED)
    
    def can_be_cancelled(self) -> bool:
        return self._state_machine.can_be_transitioned_to(SupplierOrderState.CANCELLED)
    
    def depart(self) -> None:
        self._state_machine.try_transition_to(SupplierOrderState.DEPARTED)
    
    def receive(self) -> None:
        self._state_machine.try_transition_to(SupplierOrderState.RECEIVED)
    
    def cancel(self) -> None:
        self._state_machine.try_transition_to(SupplierOrderState.CANCELLED)
