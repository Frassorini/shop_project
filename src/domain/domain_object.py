from abc import ABC
from typing import override

from domain.exceptions import DomainException


class DomainObject(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._id_: int | None = None
    
    @property
    def id_(self) -> int | None:
        return self._id_
    
    @id_.setter
    def id_(self, value: int) -> None:
        if self._id_ is not None:
            raise DomainException('id_ is immutable')
        self._id_ = value
    
    @override
    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, self.__class__):
            return False
        if self.id_ is None or value.id_ is None:
            raise DomainException('id_ field is required for eq')
        if self.id_ != value.id_:
            return False
        return True