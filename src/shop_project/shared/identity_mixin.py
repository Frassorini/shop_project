from abc import ABC
from typing import Any, Protocol, override

from shop_project.shared.entity_id import EntityId


class PIdentity(Protocol):
    @property
    def entity_id(self) -> EntityId: ...
    
    def __eq__(self, value: Any, /) -> bool: ...


class IdentityMixin(ABC, PIdentity):
    _entity_id: EntityId
    
    @property
    def entity_id(self) -> EntityId:
        return self._entity_id
    
    @override
    def __eq__(self, value: Any, /) -> bool:
        if not isinstance(value, self.__class__):
            return False
        if self.entity_id != value.entity_id:
            return False
        return True