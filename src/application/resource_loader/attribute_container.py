from typing import Any
from application.resource_loader.p_attribute_provider import PAttributeProvider


class AttributeContainer(PAttributeProvider):
    def __init__(self, attribute_name: str, attribute_values: list[Any]) -> None:
        self.attribute_name: str = attribute_name
        self._attribute_values: list[Any] = attribute_values
        
    def get(self) -> list[Any]:
        return self._attribute_values