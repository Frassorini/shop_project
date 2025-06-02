from domain.entity_mixin import EntityMixin
from domain.exceptions import NegativeAmountException
from domain.entity_id import EntityId
from domain.store_item import StoreItem


class CartItem(EntityMixin):
    def __init__(self, entity_id: EntityId, store_item: StoreItem, amount: float) -> None:
        super().__init__()
        self._entity_id: EntityId = entity_id
        self.store_item: StoreItem = store_item
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
    
    def is_chunk_of(self, item: StoreItem) -> bool:
        return item == self.store_item
