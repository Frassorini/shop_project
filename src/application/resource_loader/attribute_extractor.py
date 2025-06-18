from typing import Callable, Generic, TypeVar
from application.resource_loader.p_attribute_provider import PAttributeProvider
from application.resource_loader.load_query import LoadQuery

QueryResultType = TypeVar('QueryResultType')
ExtractedAttributeType = TypeVar('ExtractedAttributeType')

class AttributeExtractor(PAttributeProvider[ExtractedAttributeType],
                         Generic[QueryResultType, ExtractedAttributeType]):

    def __init__(self, query: LoadQuery[QueryResultType, ExtractedAttributeType],
                 attribute_name: str, 
                 strategy: Callable[[QueryResultType], list[ExtractedAttributeType]]) -> None:
        
        self.attribute_name: str = attribute_name
        self._query: LoadQuery[QueryResultType, ExtractedAttributeType] = query
        self._strategy: Callable[[QueryResultType], list[ExtractedAttributeType]] = strategy

    def get(self) -> list[ExtractedAttributeType]:
        if not self._query.is_loaded:
            raise RuntimeError("Query is not loaded")

        result: list[ExtractedAttributeType] = []
        for item in self._query.result:
            result.extend(self._strategy(item))

        return result
