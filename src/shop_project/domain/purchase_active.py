from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Self
from enum import Enum
from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.stock_item import StockItem
from shop_project.shared.identity_mixin import IdentityMixin
from shop_project.domain.exceptions import DomainException
from shop_project.shared.entity_id import EntityId
from shop_project.shared.p_snapshotable import PSnapshotable
from shop_project.shared.base_state_machine import BaseStateMachine


@dataclass(frozen=True)
class PurchaseActiveItem(StockItem, PSnapshotable):
    store_item_id: EntityId
    amount: int
    price: Decimal
    
    def to_dict(self) -> dict[str, Any]:
        return {
            'store_item_id': self.store_item_id.value,
            'amount': self.amount,
            'price': self.price,
        }
    
    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        return cls(store_item_id=EntityId(snapshot['store_item_id']), 
                   amount=snapshot['amount'], 
                   price=snapshot['price'],
                   )


class PurchaseActiveState(Enum):
    PENDING = 'PENDING'
    RESERVED = 'RESERVED'
    PAID = 'PAID'

    CLAIMED = 'CLAIMED'
    UNCLAIMED = 'UNCLAIMED'

    REFUNDED = 'REFUNDED'

    CANCELLED = 'CANCELLED'


class PurchaseActiveStateMachine(BaseStateMachine[PurchaseActiveState]):
    _transitions: dict[PurchaseActiveState, list[PurchaseActiveState]] = {
        PurchaseActiveState.PENDING: [PurchaseActiveState.RESERVED],
        PurchaseActiveState.RESERVED: [PurchaseActiveState.PAID,
                                      PurchaseActiveState.CANCELLED,],
        PurchaseActiveState.PAID: [PurchaseActiveState.CLAIMED, 
                                  PurchaseActiveState.UNCLAIMED, 
                                  PurchaseActiveState.REFUNDED],
        PurchaseActiveState.CLAIMED: [],
        PurchaseActiveState.UNCLAIMED: [PurchaseActiveState.REFUNDED],
        PurchaseActiveState.REFUNDED: [],
        PurchaseActiveState.CANCELLED: [],
    }


class PurchaseActive(BaseAggregate):
    def __init__(self, entity_id: EntityId, customer_id: EntityId, store_id: EntityId) -> None:
        self._entity_id: EntityId = entity_id
        self._state_machine: PurchaseActiveStateMachine = PurchaseActiveStateMachine(PurchaseActiveState.PENDING)
        
        self.customer_id: EntityId = customer_id
        self.store_id: EntityId = store_id
        
        self._items: dict[EntityId, PurchaseActiveItem] = {}
    
    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls(EntityId(snapshot['entity_id']), 
                  EntityId(snapshot['customer_id']), 
                  EntityId(snapshot['store_id']),
                  )
        obj._state_machine = PurchaseActiveStateMachine(PurchaseActiveState(snapshot['state']))
        
        items: list[PurchaseActiveItem] = [PurchaseActiveItem.from_dict(item) for item in snapshot['items']]
        obj._items = {item.store_item_id: item for item in items}
        
        return obj
    
    def to_dict(self) -> dict[str, Any]:
        return {'entity_id': self.entity_id.value, 
                'customer_id': self.customer_id.value, 
                'store_id': self.store_id.value, 
                'state': self.state.value, 
                'items': [item.to_dict() for item in self._items.values()],
                }
    
    def _validate_item(self, store_item_id: EntityId, price: Decimal, amount: int, store_id: EntityId) -> None:
        if store_item_id in self._items:
            raise DomainException('Item already added')
        
        if self.store_id != store_id:
            raise DomainException('Item from another store')
        
        if amount <= 0:
            raise DomainException('Amount must be > 0')
        
        if price <= 0:
            raise DomainException('Price must be > 0')
    
    def add_item(self, store_item_id: EntityId, price: Decimal, amount: int, store_id: EntityId) -> None:
        self._validate_item(store_item_id, price, amount, store_id)
        
        self._items[store_item_id] = (PurchaseActiveItem(
            store_item_id=store_item_id, 
            amount=amount, 
            price=price))
    
    def get_item(self, store_item_id: EntityId) -> PurchaseActiveItem:
        return self._items[store_item_id]
        
    def get_items(self) -> list[PurchaseActiveItem]:
        return list(self._items.values())    
    
    @property
    def state(self) -> PurchaseActiveState:
        return self._state_machine.state
    
    def can_be_reserved(self) -> bool:
        return self._state_machine.can_be_transitioned_to(PurchaseActiveState.RESERVED)
    
    def can_be_paid(self) -> bool:
        return self._state_machine.can_be_transitioned_to(PurchaseActiveState.PAID)
    
    def can_be_claimed(self) -> bool:
        return self._state_machine.can_be_transitioned_to(PurchaseActiveState.CLAIMED)
    
    def can_be_unclaimed(self) -> bool:
        return self._state_machine.can_be_transitioned_to(PurchaseActiveState.UNCLAIMED)
    
    def can_be_refunded(self) -> bool:
        return self._state_machine.can_be_transitioned_to(PurchaseActiveState.REFUNDED)
    
    def can_be_cancelled(self) -> bool:
        return self._state_machine.can_be_transitioned_to(PurchaseActiveState.CANCELLED)
    
    def reserve(self) -> None:
        self._state_machine.try_transition_to(PurchaseActiveState.RESERVED)
    
    def pay(self) -> None:
        self._state_machine.try_transition_to(PurchaseActiveState.PAID)
    
    def claim(self) -> None:
        self._state_machine.try_transition_to(PurchaseActiveState.CLAIMED)
    
    def unclaim(self) -> None:
        self._state_machine.try_transition_to(PurchaseActiveState.UNCLAIMED)
    
    def refund(self) -> None:
        self._state_machine.try_transition_to(PurchaseActiveState.REFUNDED)
    
    def cancel(self) -> None:
        self._state_machine.try_transition_to(PurchaseActiveState.CANCELLED)
