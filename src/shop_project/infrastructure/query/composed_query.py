from enum import Enum
from typing import Any, Type

from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.query.query_criteria import QueryCriteria
from shop_project.infrastructure.query.base_query import BaseQuery, QueryLock


class ComposedQuery(BaseQuery):
    def __init__(
        self,
        model_type: Type[PersistableEntity],
        criteria: QueryCriteria,
        lock: QueryLock,
    ) -> None:
        self.model_type: Type[PersistableEntity] = model_type
        self.criteria: QueryCriteria = criteria
        self.lock: QueryLock = lock
        self._result: list[PersistableEntity] = []
        self._is_loaded: bool = False

    def load(self, result: list[PersistableEntity]) -> None:
        if self._is_loaded:
            raise RuntimeError("Query is already loaded")
        
        self._result = result
        self._is_loaded = True
        
    def get_result(self) -> list[PersistableEntity]:
        if not self._is_loaded:
            raise RuntimeError("Query is not loaded")
        
        return self._result