from typing import Any, Protocol


class PValueProvider(Protocol):
    def get(self) -> list[Any]: ...
