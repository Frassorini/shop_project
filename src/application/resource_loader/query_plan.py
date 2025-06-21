from dataclasses import dataclass
from typing import Any, Self, Type, TypeVar

from application.resource_loader.attribute_extractor import AttributeExtractor
from domain.services.domain_reference_registry import DomainReferenceDescriptor, DomainReferenceRegistry

from application.resource_loader.attribute_container import AttributeContainer
from application.resource_loader.load_query import LoadQuery
from application.resource_loader.p_attribute_provider import PAttributeProvider


AttributeType = TypeVar('AttributeType')


@dataclass
class QueryData:
    model_type: type | None
    attribute_provider: PAttributeProvider | None


class QueryPlan:
    def __init__(self) -> None:
        self.domain_reference_registry: Type[DomainReferenceRegistry] = DomainReferenceRegistry
        self.queries: list[LoadQuery] = []
        self._current_query_data: QueryData = QueryData(None, None)
        self._first_query: bool = True
        
    def _build_query(self) -> None:
        if self._current_query_data.model_type is None:
            raise ValueError("No model type found")
        
        if self._current_query_data.attribute_provider is None:
            raise ValueError("No attribute provider found")
        
        self.queries.append(
            LoadQuery(self._current_query_data.model_type, 
                                self._current_query_data.attribute_provider)
        )
        
        self._current_query_data = QueryData(None, None)
    
    def load(self, entity_type: type[Any]) -> Self:
        if not self._first_query:
            self._build_query()
        else:
            self._first_query = False
        
        self._current_query_data = QueryData(entity_type, None)
        
        return self
    
    def from_attribute(self, attribute_name: str, attribute_values: list[AttributeType]) -> Self:
        attribute_container: AttributeContainer = AttributeContainer(attribute_name, attribute_values)
        
        self._current_query_data.attribute_provider = attribute_container
        
        return self
    
    def from_id(self, attribute_values: list[AttributeType]) -> Self:
        return self.from_attribute("entity_id", attribute_values)
    
    
    def from_previous(self, query_index: int | None = None) -> Self:
        if query_index is None:
            query_index = len(self.queries) - 1
        
        if query_index < 0 or query_index >= len(self.queries):
            raise ValueError("Invalid query index")
        
        if self._current_query_data.model_type is None:
            raise ValueError("No model type found")
        
        previous_query = self.queries[query_index]
        
        reference_descriptor: DomainReferenceDescriptor[Any] = self.domain_reference_registry.get_reference_descriptor(previous_query.model_type, self._current_query_data.model_type)
        
        extractor = AttributeExtractor(previous_query, reference_descriptor.attribute_name, reference_descriptor.strategy)
        
        self._current_query_data.attribute_provider = extractor
        
        return self

    
    def build(self) -> list[LoadQuery]:
        self._build_query()
        
        return self.queries