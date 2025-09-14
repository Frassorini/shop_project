from enum import Enum
from typing import Any, Type

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.infrastructure.query.query_criteria import QueryCriteria
from shop_project.infrastructure.query.base_load_query import BaseLoadQuery, QueryLock


class DomainLoadQuery(BaseLoadQuery):
    def __init__(
        self,
        model_type: Type[BaseAggregate],
        criteria: QueryCriteria,
        lock: QueryLock,
    ) -> None:
        self.model_type: Type[BaseAggregate] = model_type
        self.criteria: QueryCriteria = criteria
        self.lock: QueryLock = lock
        self._result: list[BaseAggregate] = []
        self._is_loaded: bool = False

    def load(self, result: list[BaseAggregate]) -> None:
        if self._is_loaded:
            raise RuntimeError("Query is already loaded")
        
        self._result = result
        self._is_loaded = True
        
    def get_result(self) -> list[BaseAggregate]:
        if not self._is_loaded:
            raise RuntimeError("Query is not loaded")
        
        return self._result