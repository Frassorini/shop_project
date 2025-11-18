from typing import Any, Protocol, Self, Type
from uuid import UUID

from shop_project.domain.base_aggregate import BaseAggregate


class IQueryBuilder(Protocol):
    def __init__(self, mutating: bool) -> None:
        ...
        
    def _build_query(self) -> None:
        ...
    
    # TODO interface for prebuilt queries  
    # def add_prebuilt(self, prebuilt_query: PrebuiltLoadQuery) -> Self:
    #     ...
    
    def load(self, entity_type: Type[BaseAggregate]) -> Self:
        ...
    
    def and_(self) -> Self:
        ...
    
    def or_(self) -> Self:
        ...
    
    def greater_than(self, attribute_name: str, value: str) -> Self:
        ...
    
    def from_attribute(self, attribute_name: str, attribute_values: list[Any]) -> Self:
        ...
    
    def from_id(self, attribute_values: list[UUID]) -> Self:
        ...
    
    def for_update(self) -> Self:
        ...
    
    def for_share(self) -> Self:
        ...
    
    def no_lock(self) -> Self:
        ...
    
    def from_previous(self, query_index: int | None = None) -> Self:
        ...
