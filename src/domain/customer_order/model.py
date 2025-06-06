from shared.entity_mixin import EntityMixin
from domain.exceptions import DomainException, StateException
from shared.entity_id import EntityId
from domain.customer_order.vo import CustomerOrderItem
from domain.customer_order.state import CustomerOrderState



class CustomerOrder(EntityMixin):
    def __init__(self, entity_id: EntityId, customer_id: EntityId, store: str) -> None:
        self._entity_id: EntityId = entity_id
        self.customer_id: EntityId = customer_id
        self.store: str = store
        self.state: CustomerOrderState = CustomerOrderState.PENDING
        
        self._items: dict[EntityId, CustomerOrderItem] = {}
    
    def _validate_item(self, store_item_id: EntityId, price: float, amount: int, store: str) -> None:
        if store_item_id in self._items:
            raise DomainException('Item already added')
        
        if self.store != store:
            raise DomainException('Item from another store')
        
        if amount <= 0:
            raise DomainException('Amount must be > 0')
        
        if price <= 0:
            raise DomainException('Price must be > 0')
    
    def add_item(self, store_item_id: EntityId, price: float, amount: int, store: str) -> None:
        self._validate_item(store_item_id, price, amount, store)
        
        self._items[store_item_id] = (CustomerOrderItem(
            store_item_id=store_item_id, 
            amount=amount, 
            price=price))
    
    def get_item(self, store_item_id: EntityId) -> CustomerOrderItem:
        return self._items[store_item_id]
        
    def get_items(self) -> list[CustomerOrderItem]:
        return list(self._items.values())    
    
    def _has_state(self, states: list[CustomerOrderState]) -> bool:
        return self.state in states
    
    def _ensure_has_state(self, states: list[CustomerOrderState]) -> None:
        if not self._has_state(states):
            raise StateException('Invalid state')
    
    def can_be_reserved(self) -> bool:
        return self._has_state([CustomerOrderState.PENDING])
    
    def can_be_paid(self) -> bool:
        return self._has_state([CustomerOrderState.RESERVED])
    
    def can_be_received(self) -> bool:
        return self._has_state([CustomerOrderState.PAID])
    
    def can_be_cancelled(self) -> bool:
        return self._has_state([CustomerOrderState.RESERVED, 
                                CustomerOrderState.PAID])
    
    def reserve(self) -> None:
        self._ensure_has_state([CustomerOrderState.PENDING])
        self.state = CustomerOrderState.RESERVED
    
    def pay(self) -> None:
        self._ensure_has_state([CustomerOrderState.RESERVED])
        self.state = CustomerOrderState.PAID
    
    def receive(self) -> None:
        self._ensure_has_state([CustomerOrderState.PAID])
        self.state = CustomerOrderState.RECEIVED
    
    def cancel(self) -> None:
        self._ensure_has_state([CustomerOrderState.RESERVED, 
                                CustomerOrderState.PAID])
        self.state = CustomerOrderState.CANCELLED

