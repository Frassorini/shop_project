from typing import override
from domain.entity_mixin import EntityMixin
from domain.exceptions import NegativeAmountException
from domain.entity_id import EntityId


class StoreItem(EntityMixin):
    def __init__(self, entity_id: EntityId, name: str, amount: float, store: str, price: float) -> None:
        super().__init__()
        self._entity_id: EntityId = entity_id
        self.name: str = name 
        if amount < 0:
            raise NegativeAmountException('amount field must be >= 0')
        self._amount: float = amount 
        self.store: str = store
        self.price: float = price

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


