from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Self
from enum import Enum
from shop_project.domain.persistable_entity import PersistableEntity
from shop_project.domain.stock_item import StockItem
from shop_project.shared.identity_mixin import IdentityMixin
from shop_project.domain.exceptions import DomainException
from shop_project.shared.entity_id import EntityId
from shop_project.shared.p_snapshotable import PSnapshotable
from shop_project.shared.base_state_machine import BaseStateMachine


@dataclass(frozen=True)
class PurchaseSummaryItem(PSnapshotable):
    product_id: EntityId
    amount: int
    
    def to_dict(self) -> dict[str, Any]:
        return {
            'product_id': self.product_id.value,
            'amount': self.amount,
        }
    
    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        return cls(product_id=EntityId(snapshot['product_id']), 
                   amount=snapshot['amount'], 
                   )


class PurchaseSummaryReason(Enum):
    PAYMENT_CANCELLED = "PAYMENT_CANCELLED"
    CLAIMED = "CLAIMED"
    NOT_CLAIMED = "NOT_CLAIMED"


class PurchaseSummary(PersistableEntity):
    def __init__(self, entity_id: EntityId, 
                 customer_id: EntityId, 
                 escrow_account_id: EntityId, 
                 reason: PurchaseSummaryReason, 
                 items: list[PurchaseSummaryItem]
                 ) -> None:
        self._entity_id: EntityId = entity_id
        
        self.customer_id: EntityId = customer_id
        self.escrow_account_id: EntityId = escrow_account_id
        self.reason: PurchaseSummaryReason = reason
        
        self._items: dict[EntityId, PurchaseSummaryItem] = {}
        
        for item in items:
            self._items[item.product_id] = item
    
    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls(EntityId(snapshot['entity_id']), 
                  EntityId(snapshot['customer_id']),
                  EntityId(snapshot['escrow_account_id']),
                  PurchaseSummaryReason(snapshot['reason']),
                  [PurchaseSummaryItem.from_dict(item) for item in snapshot['items']]
                  )
        
        return obj
    
    def to_dict(self) -> dict[str, Any]:
        return {'entity_id': self.entity_id.value, 
                'customer_id': self.customer_id.value,
                'escrow_account_id': self.escrow_account_id.value,
                'reason': self.reason.value,
                'items': [item.to_dict() for item in self._items.values()],
                }
    
    def get_item(self, product_id: EntityId) -> PurchaseSummaryItem:
        return self._items[product_id]
        
    def get_items(self) -> list[PurchaseSummaryItem]:
        return list(self._items.values())