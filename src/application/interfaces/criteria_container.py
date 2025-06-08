from typing import Any, Callable, Generic, TypeVar


# T = TypeVar('T')

class CriteriaContainer():
    def __init__(self, attribute: str, operator: Callable[[Any, Any], bool], values: list[Any]) -> None:
        self.attribute: str = attribute
        self.operator = operator
        self.values = values