from abc import ABC
from enum import Enum
from typing import Any, Type

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class QueryLock(Enum):
    SHARED = "SHARED"
    SHARED_NOWAIT = "SHARED_NOWAIT"
    EXCLUSIVE = "EXCLUSIVE"
    EXCLUSIVE_NOWAIT = "EXCLUSIVE_NOWAIT"
    NO_LOCK = "NO_LOCK"


class BaseQuery(ABC):
    model_type: Type[PersistableEntity]
    lock: QueryLock

    def load(self, result: Any) -> None:
        raise NotImplementedError

    def get_result(self) -> Any:
        raise NotImplementedError
