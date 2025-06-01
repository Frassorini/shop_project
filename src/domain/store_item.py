from typing import override
from domain.domain_object import DomainObject
from domain.exceptions import NegativeAmountException
from domain.p_store_item import PStoreItem


class StoreItem(DomainObject, PStoreItem):
    def __init__(self, name: str, amount: float, store: str, price: float) -> None:
        super().__init__()
        self.name: str = name 
        if amount < 0:
            raise NegativeAmountException('amount field must be >= 0')
        self._amount: float = amount 
        self.store: str = store
        self.price: float = price
    
    @property
    @override
    def amount(self) -> float:
        return self._amount
    
    @amount.setter
    def amount(self, value: float) -> None:
        if value < 0:
            raise NegativeAmountException('amount field must be >= 0')
        self._amount = value


