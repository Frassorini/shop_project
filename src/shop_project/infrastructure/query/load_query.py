from enum import Enum
from typing import Any, Type

from shop_project.domain.p_aggregate import PAggregate
from shop_project.infrastructure.query.query_criteria import QueryCriteria

# Под капотом в репозиториях все равно должен использоваться advisory lock
# в дополнение к классическим блокировкам для приоритизации запросов на запись
class QueryLock(Enum):
    FOR_SHARE = 'FOR SHARE'
    FOR_UPDATE = 'FOR UPDATE'
    NO_LOCK = 'NO LOCK'


class LoadQuery():
    def __init__(
        self,
        model_type: Type[PAggregate],
        criteria: QueryCriteria,
        lock: QueryLock,
    ) -> None:
        self.model_type: Type[PAggregate] = model_type
        self.criteria: QueryCriteria = criteria
        self.lock: QueryLock = lock
        self._result: list[PAggregate] = []
        self._is_loaded: bool = False

    def load(self, result: list[PAggregate]) -> None:
        if self._is_loaded:
            raise RuntimeError("Query is already loaded")
        
        self._result = result
        self._is_loaded = True
        
    def get_result(self) -> list[PAggregate]:
        if not self._is_loaded:
            raise RuntimeError("Query is not loaded")
        
        return self._result