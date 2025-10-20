from dataclasses import dataclass
from typing import Any, Self
from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.shared.identity_mixin import IdentityMixin
from shop_project.shared.entity_id import EntityId
from shop_project.domain.exceptions import DomainException
from shop_project.shared.p_snapshotable import PSnapshotable


@dataclass(frozen=True)
class PurchaseDraftItem(PSnapshotable):
    store_item_id: EntityId
    amount: int
    
    def to_dict(self) -> dict[str, Any]:
        return {'store_item_id': self.store_item_id.value, 'amount': self.amount}

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        return cls(EntityId(snapshot['store_item_id']), snapshot['amount'])


class PurchaseDraft(BaseAggregate):
    def __init__(self, entity_id: EntityId, customer_id: EntityId) -> None:
        super().__init__()
        self._entity_id: EntityId = entity_id
        self.customer_id: EntityId = customer_id
        self._items: dict[EntityId, PurchaseDraftItem] = {}
    
    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls(EntityId(snapshot['entity_id']),
                  EntityId(snapshot['customer_id']),
        )
        
        items: list[PurchaseDraftItem] = [PurchaseDraftItem.from_dict(item) for item in snapshot['items']]
        obj._items = {item.store_item_id: item for item in items}
        
        return obj
    
    def to_dict(self) -> dict[str, Any]:
        return {'entity_id': self.entity_id.value, 
                'customer_id': self.customer_id.value,
                'items': [item.to_dict() for item in self._items.values()],
                }
    
    def _validate_item(self, store_item_id: EntityId, amount: int) -> None:
        if store_item_id in self._items:
            raise DomainException('Item already added')
        
        if amount <= 0:
            raise DomainException('Amount must be > 0')
    
    def add_item(self, store_item_id: EntityId, amount: int) -> None:
        self._validate_item(store_item_id, amount)
        
        self._items[store_item_id] = (PurchaseDraftItem(
            store_item_id=store_item_id, 
            amount=amount,))
    
    def get_item(self, store_item_id: EntityId) -> PurchaseDraftItem:
        return self._items[store_item_id]
        
    def get_items(self) -> list[PurchaseDraftItem]:
        return list(self._items.values())
