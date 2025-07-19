from dataclasses import dataclass
from typing import Any, Self
from shop_project.shared.identity_mixin import IdentityMixin
from shop_project.shared.entity_id import EntityId
from shop_project.domain.exceptions import DomainException
from shop_project.shared.p_snapshotable import PSnapshotable


@dataclass(frozen=True)
class CartItem(PSnapshotable):
    store_item_id: EntityId
    amount: int
    
    def snapshot(self) -> dict[str, str]:
        return {'store_item_id': self.store_item_id.to_str(), 'amount': str(self.amount)}

    @classmethod
    def from_snapshot(cls, snapshot: dict[str, str]) -> Self:
        return cls(EntityId(snapshot['store_item_id']), int(snapshot['amount']))


class Cart(IdentityMixin, PSnapshotable):
    def __init__(self, entity_id: EntityId, customer_id: EntityId, store_id: EntityId) -> None:
        super().__init__()
        self._entity_id: EntityId = entity_id
        self.customer_id: EntityId = customer_id
        self.store_id: EntityId = store_id
        self._items: dict[EntityId, CartItem] = {}
    
    @classmethod
    def from_snapshot(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls(EntityId(snapshot['entity_id']),
                  EntityId(snapshot['customer_id']),
                  EntityId(snapshot['store_id']),
        )
        
        items: list[CartItem] = [CartItem.from_snapshot(item) for item in snapshot['items']]
        obj._items = {item.store_item_id: item for item in items}
        
        return obj
    
    def snapshot(self) -> dict[str, str | list[dict[str, str]]]:
        return {'entity_id': self.entity_id.to_str(), 
                'customer_id': self.customer_id.to_str(), 
                'store_id': self.store_id.to_str(), 
                'items': [item.snapshot() for item in self._items.values()],
                }
    
    def _validate_item(self, store_item_id: EntityId, amount: int, store_id: EntityId) -> None:
        if store_item_id in self._items:
            raise DomainException('Item already added')
        
        if self.store_id != store_id:
            raise DomainException('Item from another store')
        
        if amount <= 0:
            raise DomainException('Amount must be > 0')
    
    def add_item(self, store_item_id: EntityId, amount: int, store_id: EntityId) -> None:
        self._validate_item(store_item_id, amount, store_id)
        
        self._items[store_item_id] = (CartItem(
            store_item_id=store_item_id, 
            amount=amount,))
    
    def get_item(self, store_item_id: EntityId) -> CartItem:
        return self._items[store_item_id]
        
    def get_items(self) -> list[CartItem]:
        return list(self._items.values())
