from typing import Any, Generic, TypeVar
from application.resource_loader.p_attribute_provider import PAttributeProvider


T = TypeVar('T')

class AttributeContainer(PAttributeProvider[T], Generic[T]):
    def __init__(self, attribute_name: str, attribute_values: list[T]) -> None:
        self.attribute_name: str = attribute_name
        self._attribute_values: list[T] = attribute_values
        
    def get(self) -> list[T]:
        return self._attribute_values