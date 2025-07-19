from dataclasses import dataclass
from typing import Any, Self, cast


@dataclass(frozen=True)
class EntityId:
    value: str

    def __post_init__(self):
        if not isinstance(cast(Any, self.value), str):
            raise TypeError(f"EntityId.value must be str, got {type(self.value).__name__}")

    def to_str(self, /) -> str:
        return str(self.value)
