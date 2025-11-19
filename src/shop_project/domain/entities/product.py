from decimal import Decimal
from typing import Any
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.shared.identity_mixin import IdentityMixin
from shop_project.domain.exceptions import NegativeAmountException
from shop_project.shared.entity_id import EntityId
from shop_project.shared.p_snapshotable import PSnapshotable


class Product(PersistableEntity):
    def __init__(self, entity_id: EntityId, name: str, amount: int, price: Decimal) -> None:
        super().__init__()
        self._entity_id: EntityId = entity_id
        self.name: str = name 
        if amount < 0:
            raise NegativeAmountException('amount field must be >= 0')
        self._amount: int = amount 
        self.price: Decimal = price
    
    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> 'Product':
        return cls(
            entity_id=EntityId(snapshot['entity_id']), 
            name=snapshot['name'], 
            amount=snapshot['amount'],
            price=snapshot['price']
        )
    
    def to_dict(self) -> dict[str, Any]:
        return {
            'entity_id': self.entity_id.value,
            'name': self.name,
            'amount': self._amount,
            'price': self.price
        }

    def reserve(self, amount: int) -> None:
        self.amount -= amount
        
    def restock(self, amount: int) -> None:
        self.amount += amount
    
    @property
    def amount(self) -> int:
        return self._amount
    
    @amount.setter
    def amount(self, value: int) -> None:
        if value < 0:
            raise NegativeAmountException('amount field must be >= 0')
        self._amount = value


