from typing import Any, Callable
from infrastructure.query.p_attribute_provider import PAttributeProvider
from infrastructure.query.load_query import LoadQuery


class AttributeExtractor(PAttributeProvider):
    def __init__(self, query: LoadQuery,
                 attribute_name: str, 
                 strategy: Callable[[Any], list[Any]]) -> None:
        
        self.attribute_name: str = attribute_name
        self._query: LoadQuery = query
        self._strategy: Callable[[Any], list[Any]] = strategy

    def get(self) -> list[Any]:
        if not self._query.is_loaded:
            raise RuntimeError("Query is not loaded")

        result: list[Any] = []
        for item in self._query.result:
            result.extend(self._strategy(item))

        return result
