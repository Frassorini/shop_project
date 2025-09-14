from typing import Literal, Type

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.infrastructure.query.query_criteria import QueryCriteria
from shop_project.infrastructure.query.base_load_query import BaseLoadQuery, QueryLock

class PrebuiltLoadQuery(BaseLoadQuery):
    return_type: Literal["DOMAIN", "SCALARS"]
    def __init__(
        self,
        lock: Literal["NO_LOCK", "EXCLUSIVE", "SHARED"],
    ) -> None:
        self.lock: QueryLock = QueryLock(lock)
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
    
    def set_args(self) -> None:
        pass