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
class ShipmentSummaryItem(StockItem, PSnapshotable):
    store_item_id: EntityId
    amount: int
    
    def to_dict(self) -> dict[str, Any]:
        return {
            'store_item_id': self.store_item_id.value,
            'amount': self.amount,
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        return cls(EntityId(snapshot['store_item_id']), snapshot['amount'])

    def _validate(self) -> None:
        if self.amount <= 0:
            raise DomainException('Amount must be > 0')


class ShipmentSummaryReason(Enum):
    RECEIVED = 'RECEIVED'
    CANCELLED = 'CANCELLED'


class ShipmentSummary(BaseAggregate):
    def __init__(self, entity_id: EntityId, 
                 reason: ShipmentSummaryReason,
                 items: list[ShipmentSummaryItem]) -> None:
        self._entity_id: EntityId = entity_id
        self.reason = reason
        
        self._items: dict[EntityId, ShipmentSummaryItem] = {}
        
        for item in items:
            self._validate_item(item)
            self._items[item.store_item_id] = item
    
    def to_dict(self) -> dict[str, Any]:
        return {'entity_id': self.entity_id.value, 
                'reason': self.reason.value,
                'items': [item.to_dict() for item in self._items.values()],
                }
    
    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls(EntityId(snapshot['entity_id']), 
                  ShipmentSummaryReason(snapshot['reason']),
                  [ShipmentSummaryItem.from_dict(item) for item in snapshot['items']]
                  )
        return obj
        
    def _validate_item(self, item: ShipmentSummaryItem) -> None:
        if item.store_item_id in self._items:
            raise DomainException('Item already added')
    
    def get_item(self, store_item_id: EntityId) -> ShipmentSummaryItem:
        return self._items[store_item_id]
        
    def get_items(self) -> list[ShipmentSummaryItem]:
        return list(self._items.values())