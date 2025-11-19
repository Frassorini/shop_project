from typing import Any

from shop_project.infrastructure.query.p_value_provider import PValueProvider


class ValueContainer(PValueProvider):
    def __init__(self, attribute_values: list[Any]) -> None:
        self._attribute_values: list[Any] = attribute_values

    def get(self) -> list[Any]:
        return self._attribute_values
