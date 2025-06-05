from domain.cart import Cart
from domain.entity_mixin import EntityMixin
from domain.exceptions import DomainException
from domain.entity_id import EntityId


class Customer(EntityMixin):
    def __init__(self, entity_id: EntityId, name: str) -> None:
        super().__init__()
        self._entity_id: EntityId = entity_id
        self.name: str = name
        
