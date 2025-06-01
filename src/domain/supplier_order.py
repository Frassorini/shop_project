from datetime import datetime
from typing import Self

from domain.exceptions import DomainException
from domain.supplier_order_item import SupplierOrderItem
from domain.base_order import Order, OrderState


class SupplierOrderState(OrderState):
    PENDING = 'PENDING'
    DEPARTED = 'DEPARTED'
    RECEIVED = 'RECEIVED'
    CANCELLED = 'CANCELLED'


class SupplierOrder(Order):
    def __init__(self, store: str) -> None:
        super().__init__()
        self._items: list[SupplierOrderItem] = []
        self.state: SupplierOrderState = SupplierOrderState.PENDING
        self.store: str = store
        self.departure: datetime | None = None
        self.arrival: datetime | None = None
    
    @property
    def items(self) -> list[SupplierOrderItem]:
        return self._items
    
    @Order._state_required(allowed_states=[SupplierOrderState.PENDING])
    def depart(self, departure: datetime, arrival: datetime) -> None:
        self.departure = departure
        self.arrival = arrival
        self.state = SupplierOrderState.DEPARTED
        
    @Order._state_required(allowed_states=[SupplierOrderState.DEPARTED])
    def receive(self) -> None:
        for item in self._items:
            item.receive()
        self.state = SupplierOrderState.RECEIVED
    
    def cancel(self) -> None:
        self.state = SupplierOrderState.CANCELLED
    
    def __add__(self, other: SupplierOrderItem) -> Self:
        if other.store != self.store:
            raise DomainException('Items must be from the same store')
        self._items.append(other)
        return self
    
    def __sub__(self, other: SupplierOrderItem) -> Self:
        if other.store != self.store:
            raise DomainException('Items must be from the same store')
        self._items.remove(other)
        return self