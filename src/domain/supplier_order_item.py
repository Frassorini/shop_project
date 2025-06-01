from domain.domain_object import DomainObject
from domain.exceptions import StateException
from domain.p_store_item import PStoreItem


class SupplierOrderItem(DomainObject):
    def __init__(self, store_item: PStoreItem, amount: int) -> None:
        super().__init__()
        self.store_item: PStoreItem = store_item
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
