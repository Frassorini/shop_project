from dataclasses import dataclass
from enum import Enum
from typing import Any, Self
from shop_project.domain.persistable_entity import PersistableEntity
from shop_project.domain.stock_item import StockItem
from shop_project.shared.base_state_machine import BaseStateMachine
from shop_project.shared.identity_mixin import IdentityMixin
from shop_project.shared.entity_id import EntityId
from shop_project.domain.exceptions import DomainException
from shop_project.shared.p_snapshotable import PSnapshotable


@dataclass(frozen=True)
class PurchaseDraftItem(PSnapshotable, StockItem):
    product_id: EntityId
    amount: int
    
    def to_dict(self) -> dict[str, Any]:
        return {'product_id': self.product_id.value, 'amount': self.amount}

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        return cls(EntityId(snapshot['product_id']), snapshot['amount'])


class PurchaseDraftState(Enum):
    ACTIVE = 'ACTIVE'
    FINALIZED = 'FINALIZED'


class PurchaseDraftStateMachine(BaseStateMachine[PurchaseDraftState]):
    _transitions = {
        PurchaseDraftState.ACTIVE: [PurchaseDraftState.FINALIZED],
    }


class PurchaseDraft(PersistableEntity):
    def __init__(self, entity_id: EntityId, customer_id: EntityId) -> None:
        super().__init__()
        self._entity_id: EntityId = entity_id
        self.customer_id: EntityId = customer_id
        self._items: dict[EntityId, PurchaseDraftItem] = {}
        self._state_machine = PurchaseDraftStateMachine(PurchaseDraftState.ACTIVE)
    
    @property
    def state(self) -> PurchaseDraftState:
        return self._state_machine.state
    
    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls(EntityId(snapshot['entity_id']),
                  EntityId(snapshot['customer_id']),
        )
        obj._state_machine = PurchaseDraftStateMachine(PurchaseDraftState(snapshot['state']))
        items: list[PurchaseDraftItem] = [PurchaseDraftItem.from_dict(item) for item in snapshot['items']]
        obj._items = {item.product_id: item for item in items}
        
        return obj
    
    def to_dict(self) -> dict[str, Any]:
        return {'entity_id': self.entity_id.value, 
                'customer_id': self.customer_id.value,
                'state': self.state.value,
                'items': [item.to_dict() for item in self._items.values()],
                }
    
    def _validate_item(self, product_id: EntityId, amount: int) -> None:
        if product_id in self._items:
            raise DomainException('Item already added')
        
        if amount <= 0:
            raise DomainException('Amount must be > 0')
    
    def add_item(self, product_id: EntityId, amount: int) -> None:
        if self.state == PurchaseDraftState.FINALIZED:
            raise DomainException('Cannot add item to finalized draft')
        
        self._validate_item(product_id, amount)
        
        self._items[product_id] = (PurchaseDraftItem(
            product_id=product_id, 
            amount=amount,))
    
    def get_item(self, product_id: EntityId) -> PurchaseDraftItem:
        return self._items[product_id]
        
    def get_items(self) -> list[PurchaseDraftItem]:
        return list(self._items.values())
    
    def finalize(self) -> None:
        self._state_machine.try_transition_to(PurchaseDraftState.FINALIZED)
    
    def is_finalized(self) -> bool:
        return self.state == PurchaseDraftState.FINALIZED
    
    def is_active(self) -> bool:
        return self.state == PurchaseDraftState.ACTIVE
