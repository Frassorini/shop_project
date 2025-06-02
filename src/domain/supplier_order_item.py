from domain.entity_mixin import EntityMixin
from domain.exceptions import StateException
from domain.store_item import StoreItem
from domain.entity_id import EntityId


class SupplierOrderItem(EntityMixin):
    def __init__(self, entity_id: EntityId, store_item: StoreItem, amount: int) -> None:
        super().__init__()
        self._entity_id: EntityId = entity_id
        self.store_item: StoreItem = store_item
        self.amount: int = amount
        self._received: bool = False
    
    @property
    def received(self) -> bool:
        return self._received

    @property
    def store(self) -> str:
        return self.store_item.store
    
    def receive(self) -> None:
        if self._received:
            raise StateException("Item already received")
        self.store_item.amount += self.amount
        self._received = True
