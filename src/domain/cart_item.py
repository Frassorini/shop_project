from domain.domain_object import DomainObject
from domain.exceptions import NegativeAmountException
from domain.p_store_item import PStoreItem


class CartItem(DomainObject):
    def __init__(self, store_item: PStoreItem, amount: float) -> None:
        super().__init__()
        self.store_item: PStoreItem = store_item
        self.name: str = store_item.name
        if amount < 0:
            raise NegativeAmountException('amount field must be >= 0')
        self._amount: float = amount 
    
    @property
    def amount(self) -> float:
        return self._amount
    
    @amount.setter
    def amount(self, value: float) -> None:
        if value < 0:
            raise NegativeAmountException('amount field must be >= 0')
        self._amount = value
    
    @property
    def price(self) -> float:
        return self.store_item.price * self.amount
    
    def is_chunk_of(self, item: PStoreItem) -> bool:
        return item == self.store_item
