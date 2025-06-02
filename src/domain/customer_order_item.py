from enum import Enum
from functools import wraps
from domain.entity_mixin import EntityMixin
from domain.exceptions import DomainException, NegativeAmountException, StateException
from domain.store_item import StoreItem
from domain.entity_id import EntityId


class CustomerOrderItemState(Enum):
    PENDING = 'PENDING'
    RESERVED = 'RESERVED'
    FINALIZED = 'FINALIZED'


def _state_required(allowed_states: list[CustomerOrderItemState]):
    def wrapped(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if hasattr(args[0], 'state') and args[0].state in allowed_states:
                return func(*args, **kwargs)
            else:
                raise StateException('Invalid state to perform action')
        return wrapper
    return wrapped


class CustomerOrderItem(EntityMixin):
    def __init__(self, entity_id: EntityId, store_item: StoreItem, amount: float) -> None:
        super().__init__()
        self._entity_id: EntityId = entity_id
        self.store_item: StoreItem = store_item
        self.name: str = store_item.name
        if amount < 0:
            raise NegativeAmountException('amount field must be >= 0')
        self.amount: float = amount
        self._reserved_price_per_one: float | None = None
        self.state: CustomerOrderItemState = CustomerOrderItemState.PENDING
    
    @property
    def store(self) -> str:
        return self.store_item.store
    
    @property
    def price_per_one(self) -> float:
        if self._reserved_price_per_one is not None:
            return self._reserved_price_per_one
        return self.store_item.price
    
    @property
    def price(self) -> float:
        return self.amount * self.price_per_one
    
    def is_chunk_of(self, item: StoreItem) -> bool:
        return item == self.store_item

    @_state_required(allowed_states=[CustomerOrderItemState.PENDING])
    def reserve(self) -> None:
        try:
            self.store_item.amount -= self.amount
            self._reserved_price_per_one = self.store_item.price
        except NegativeAmountException as e:
            raise DomainException() from e
        self.state = CustomerOrderItemState.RESERVED
    
    @_state_required(allowed_states=[CustomerOrderItemState.RESERVED])
    def cancel(self) -> None:
        self.store_item.amount += self.amount
        self.state = CustomerOrderItemState.FINALIZED

    @_state_required(allowed_states=[CustomerOrderItemState.RESERVED])
    def finalize(self) -> None:
        self.state = CustomerOrderItemState.FINALIZED