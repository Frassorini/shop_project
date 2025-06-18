from typing import Callable, Generic, TypeVar


T = TypeVar('T')

class AttributeCriterion(Generic[T]):
    def __init__(self, operator: Callable[[T, T], bool], values: list[T]) -> None:
        self.operator = operator
        self.values = values
    
    def apply(self, Attribute_values: list[T]) -> list[T]:
        return [item for item in Attribute_values if any(self.operator(item, value) for value in self.values)]