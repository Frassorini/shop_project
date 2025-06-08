from typing import Callable, Generic, TypeVar
from application.interfaces.p_criteria_provider import PCriteriaProvider
from application.interfaces.load_query import LoadQuery
from shared.entity_id import EntityId

T = TypeVar('T')

class IdExtractor(PCriteriaProvider, Generic[T]):
    def __init__(self, query: LoadQuery[T], strategy: Callable[[T], list[EntityId]]) -> None:
        self._query: LoadQuery[T] = query
        self._strategy: Callable[[T], list[EntityId]] = strategy
    
    def extract(self) -> list[EntityId]:
        # STUB
        return self._strategy(self._query.result[0])