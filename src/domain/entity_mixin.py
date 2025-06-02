from abc import ABC
from typing import override

from domain.exceptions import DomainException
from domain.entity_id import EntityId


class EntityMixin(ABC):
    _entity_id: EntityId
    
    @property
    def id_(self) -> int:
        return self._entity_id.value
    
    @override
    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, self.__class__):
            return False
        if self.id_ != value.id_:
            return False
        return True