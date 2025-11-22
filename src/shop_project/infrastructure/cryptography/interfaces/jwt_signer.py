from typing import Any, Protocol


class JWTSigner(Protocol):
    def sign(self, payload: dict[str, Any]) -> str: ...

    def verify(self, data: str) -> dict[str, Any]: ...
