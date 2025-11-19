from abc import ABC
from enum import Enum
from typing import Any, Literal, Self, Type

from shop_project.domain.persistable_entity import PersistableEntity
from shop_project.infrastructure.query.query_criteria import QueryCriteria


class QueryLock(Enum):
    SHARED = 'SHARED'
    EXCLUSIVE = 'EXCLUSIVE'
    NO_LOCK = 'NO_LOCK'


class BaseQuery(ABC):
    model_type: Type[PersistableEntity]
    lock: QueryLock

    def load(self, result: Any) -> None:
        raise NotImplementedError
        
    def get_result(self) -> Any:
        raise NotImplementedError