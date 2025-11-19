from typing import Any, Protocol, Self


class PSnapshotable(Protocol):
    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self: ...
