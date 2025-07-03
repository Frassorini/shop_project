from typing import Any
from shared.identity_mixin import IdentityMixin
from domain.exceptions import NegativeAmountException
from shared.entity_id import EntityId
from shared.p_snapshotable import PSnapshotable


class StoreItem(IdentityMixin, PSnapshotable):
    def __init__(self, entity_id: EntityId, name: str, amount: float, store_id: EntityId, price: float) -> None:
        super().__init__()
        self._entity_id: EntityId = entity_id
        self.name: str = name 
        if amount < 0:
            raise NegativeAmountException('amount field must be >= 0')
        self._amount: float = amount 
        self.store_id: EntityId = store_id
        self.price: float = price
    
    @classmethod
    def from_snapshot(cls, snapshot: dict[str, Any]) -> 'StoreItem':
        return cls(
            entity_id=EntityId(snapshot['entity_id']), 
            name=snapshot['name'], 
            amount=snapshot['amount'], 
            store_id=EntityId(snapshot['store_id']), 
            price=snapshot['price'])
    
    def snapshot(self) -> dict[str, Any]:
        return {
            'entity_id': self.entity_id.to_str(),
            'name': self.name,
            'amount': self._amount,
            'store_id': self.store_id.to_str(),
            'price': self.price
        }

    def reserve(self, amount: float) -> None:
        self.amount -= amount
        
    def restock(self, amount: float) -> None:
        self.amount += amount
    
    @property
    def amount(self) -> float:
        return self._amount
    
    @amount.setter
    def amount(self, value: float) -> None:
        if value < 0:
            raise NegativeAmountException('amount field must be >= 0')
        self._amount = value


