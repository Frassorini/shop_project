from typing import Self

from domain.customer_order_item import CustomerOrderItem, CustomerOrderItemState
from domain.customer import Customer
from domain.entity_mixin import EntityMixin
from domain.exceptions import DomainException
from domain.base_order import Order, OrderState
from domain.entity_id import EntityId


class CustomerOrderState(OrderState):
    PENDING = 'PENDING'
    RESERVED = 'RESERVED'
    PAID = 'PAID'
    RECEIVED = 'RECEIVED'
    CANCELLED = 'CANCELLED'


class CustomerOrder(Order, EntityMixin):
    def __init__(self, entity_id: EntityId, customer: Customer, store: str) -> None:
        super().__init__()
        self._entity_id: EntityId = entity_id
        self.customer: Customer = customer
        self.items: list[CustomerOrderItem] = []
        self.state: CustomerOrderState = CustomerOrderState.PENDING
        self.store: str = store
    
    @property
    def price(self) -> float:
        return sum([item.price for item in self.items])
    
    @Order._state_required(allowed_states=[CustomerOrderState.PENDING])
    def reserve(self) -> None:
        for item in self.items:
            item.reserve()

        if self.items == []:
            raise DomainException('Empty order is not allowed')

        self.state = CustomerOrderState.RESERVED
    
    @Order._state_required(allowed_states=[CustomerOrderState.RESERVED, CustomerOrderState.PAID])
    def cancel(self) -> None:      
        for item in self.items:
            item.cancel()
            
        self.state = CustomerOrderState.CANCELLED
    
    @Order._state_required(allowed_states=[CustomerOrderState.RESERVED])
    def pay(self) -> None:      
        self.state = CustomerOrderState.PAID
        
    @Order._state_required(allowed_states=[CustomerOrderState.PAID])
    def receive(self, receiver: Customer) -> None:
        if receiver != self.customer:
            raise DomainException("Attempted to receive other's order")
        
        self.state = CustomerOrderState.RECEIVED
    
    def __add__(self, other: CustomerOrderItem) -> Self:
        if other.store != self.store:
            raise DomainException('Items must be from the same store')
        if other.state != CustomerOrderItemState.PENDING:
            raise DomainException('Item is not pending')
        self.items.append(other)
        return self
    
    def __sub__(self, other: CustomerOrderItem) -> Self:
        if other.state != CustomerOrderItemState.PENDING:
            raise DomainException('Item is not pending')
        self.items.remove(other)
        return self