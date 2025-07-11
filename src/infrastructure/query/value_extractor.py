from typing import Any, Callable
from infrastructure.query.p_value_provider import PValueProvider
from infrastructure.query.load_query import LoadQuery


class ValueExtractor(PValueProvider):
    def __init__(self, query: LoadQuery,
                 strategy: Callable[[Any], list[Any]]) -> None:
        
        self._query: LoadQuery = query
        self._strategy: Callable[[Any], list[Any]] = strategy

    def get(self) -> list[Any]:
        result: list[Any] = []
        for item in self._query.get_result():
            result.extend(self._strategy(item))

        return result
