from abc import ABC
from typing import Any, override
from uuid import UUID


class IdentityMixin(ABC):
    entity_id: UUID

    @override
    def __eq__(self, value: Any, /) -> bool:
        if not isinstance(value, self.__class__):
            return False
        if self.entity_id != value.entity_id:
            return False
        return True
