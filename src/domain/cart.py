from collections.abc import Iterator
from dataclasses import dataclass
from typing import Self
from domain.entity_mixin import EntityMixin
from domain.entity_id import EntityId
from domain.exceptions import DomainException


@dataclass(frozen=True)
class CartItem:
    store_item_id: EntityId
    amount: int


class Cart(EntityMixin):
    def __init__(self, entity_id: EntityId, customer_id: EntityId, store: str) -> None:
        super().__init__()
        self._entity_id: EntityId = entity_id
        self.customer_id: EntityId = customer_id
        self.store: str = store
        self._items: dict[EntityId, CartItem] = {}
    
    def _validate_item(self, store_item_id: EntityId, amount: int, store: str) -> None:
        if store_item_id in self._items:
            raise DomainException('Item already added')
        
        if self.store != store:
            raise DomainException('Item from another store')
        
        if amount <= 0:
            raise DomainException('Amount must be > 0')
    
    def add_item(self, store_item_id: EntityId, amount: int, store: str) -> None:
        self._validate_item(store_item_id, amount, store)
        
        self._items[store_item_id] = (CartItem(
            store_item_id=store_item_id, 
            amount=amount,))
    
    def get_item(self, store_item_id: EntityId) -> CartItem:
        return self._items[store_item_id]
        
    def get_items(self) -> list[CartItem]:
        return list(self._items.values())    