from abc import ABC
from typing import override

from domain.exceptions import DomainException
from domain.entity_id import EntityId


class EntityMixin(ABC):
    _entity_id: EntityId
    
    @property
    def entity_id(self) -> EntityId:
        return self._entity_id
    
    @override
    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, self.__class__):
            return False
        if self.entity_id != value.entity_id:
            return False
        return True