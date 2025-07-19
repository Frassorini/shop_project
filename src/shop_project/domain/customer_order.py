from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Self
from enum import Enum
from shop_project.domain.stock_item import StockItem
from shop_project.shared.identity_mixin import IdentityMixin
from shop_project.domain.exceptions import DomainException
from shop_project.shared.entity_id import EntityId
from shop_project.shared.p_snapshotable import PSnapshotable
from shop_project.shared.base_state_machine import BaseStateMachine


@dataclass(frozen=True)
class CustomerOrderItem(StockItem, PSnapshotable):
    store_item_id: EntityId
    amount: int
    price: Decimal
    
    def snapshot(self) -> dict[str, str]:
        return {
            'store_item_id': self.store_item_id.to_str(),
            'amount': str(self.amount),
            'price': str(self.price),
        }
    
    @classmethod
    def from_snapshot(cls, snapshot: dict[str, str]) -> Self:
        return cls(store_item_id=EntityId(snapshot['store_item_id']), 
                   amount=int(snapshot['amount']), 
                   price=Decimal(snapshot['price']),
                   )


class CustomerOrderState(Enum):
    PENDING = 'PENDING'
    RESERVED = 'RESERVED'
    PAID = 'PAID'

    CLAIMED = 'CLAIMED'
    UNCLAIMED = 'UNCLAIMED'

    REFUNDED = 'REFUNDED'

    CANCELLED = 'CANCELLED'


class CustomerOrderStateMachine(BaseStateMachine[CustomerOrderState]):
    _transitions: dict[CustomerOrderState, list[CustomerOrderState]] = {
        CustomerOrderState.PENDING: [CustomerOrderState.RESERVED],
        CustomerOrderState.RESERVED: [CustomerOrderState.PAID,
                                      CustomerOrderState.CANCELLED,],
        CustomerOrderState.PAID: [CustomerOrderState.CLAIMED, 
                                  CustomerOrderState.UNCLAIMED, 
                                  CustomerOrderState.REFUNDED],
        CustomerOrderState.CLAIMED: [],
        CustomerOrderState.UNCLAIMED: [CustomerOrderState.REFUNDED],
        CustomerOrderState.REFUNDED: [],
        CustomerOrderState.CANCELLED: [],
    }


class CustomerOrder(PSnapshotable, IdentityMixin,):
    def __init__(self, entity_id: EntityId, customer_id: EntityId, store_id: EntityId) -> None:
        self._entity_id: EntityId = entity_id
        self._state_machine: CustomerOrderStateMachine = CustomerOrderStateMachine(CustomerOrderState.PENDING)
        
        self.customer_id: EntityId = customer_id
        self.store_id: EntityId = store_id
        
        self._items: dict[EntityId, CustomerOrderItem] = {}
    
    @classmethod
    def from_snapshot(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls(EntityId(snapshot['entity_id']), 
                  EntityId(snapshot['customer_id']), 
                  EntityId(snapshot['store_id']),
                  )
        obj._state_machine = CustomerOrderStateMachine(CustomerOrderState(snapshot['state']))
        
        items: list[CustomerOrderItem] = [CustomerOrderItem.from_snapshot(item) for item in snapshot['items']]
        obj._items = {item.store_item_id: item for item in items}
        
        return obj
    
    def snapshot(self) -> dict[str, str | list[dict[str, str]]]:
        return {'entity_id': self.entity_id.to_str(), 
                'customer_id': self.customer_id.to_str(), 
                'store_id': self.store_id.to_str(), 
                'state': self.state.value, 
                'items': [item.snapshot() for item in self._items.values()],
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
        
        self._items[store_item_id] = (CustomerOrderItem(
            store_item_id=store_item_id, 
            amount=amount, 
            price=price))
    
    def get_item(self, store_item_id: EntityId) -> CustomerOrderItem:
        return self._items[store_item_id]
        
    def get_items(self) -> list[CustomerOrderItem]:
        return list(self._items.values())    
    
    @property
    def state(self) -> CustomerOrderState:
        return self._state_machine.state
    
    def can_be_reserved(self) -> bool:
        return self._state_machine.can_be_transitioned_to(CustomerOrderState.RESERVED)
    
    def can_be_paid(self) -> bool:
        return self._state_machine.can_be_transitioned_to(CustomerOrderState.PAID)
    
    def can_be_claimed(self) -> bool:
        return self._state_machine.can_be_transitioned_to(CustomerOrderState.CLAIMED)
    
    def can_be_unclaimed(self) -> bool:
        return self._state_machine.can_be_transitioned_to(CustomerOrderState.UNCLAIMED)
    
    def can_be_refunded(self) -> bool:
        return self._state_machine.can_be_transitioned_to(CustomerOrderState.REFUNDED)
    
    def can_be_cancelled(self) -> bool:
        return self._state_machine.can_be_transitioned_to(CustomerOrderState.CANCELLED)
    
    def reserve(self) -> None:
        self._state_machine.try_transition_to(CustomerOrderState.RESERVED)
    
    def pay(self) -> None:
        self._state_machine.try_transition_to(CustomerOrderState.PAID)
    
    def claim(self) -> None:
        self._state_machine.try_transition_to(CustomerOrderState.CLAIMED)
    
    def unclaim(self) -> None:
        self._state_machine.try_transition_to(CustomerOrderState.UNCLAIMED)
    
    def refund(self) -> None:
        self._state_machine.try_transition_to(CustomerOrderState.REFUNDED)
    
    def cancel(self) -> None:
        self._state_machine.try_transition_to(CustomerOrderState.CANCELLED)
