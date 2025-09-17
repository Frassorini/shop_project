from typing import Any, Callable
from shop_project.infrastructure.query.p_value_provider import PValueProvider
from shop_project.infrastructure.query.base_load_query import BaseLoadQuery


class ValueExtractor(PValueProvider):
    def __init__(self, query: BaseLoadQuery,
                 strategy: Callable[[Any], list[Any]]) -> None:
        
        self._query: BaseLoadQuery = query
        self._strategy: Callable[[Any], list[Any]] = strategy

    def get(self) -> list[Any]:
        result: list[Any] = []
        for item in self._query.get_result():
            result.extend(self._strategy(item))

        return result
