from typing import Any, Protocol


class PAttributeProvider(Protocol):
    attribute_name: str
    def get(self) -> list[Any]:
        ...