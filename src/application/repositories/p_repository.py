from typing import Any, Protocol, Generic, Type, TypeVar

from shared.entity_id import EntityId

T = TypeVar("T")

class PRepository(Protocol, Generic[T]):
    model_type: Type[T]
    
    def get_by_criteria(self, criteria: str, values: list[Any]) -> list[T]: ...
    
    def fill(self, items: list[T]) -> None: ...