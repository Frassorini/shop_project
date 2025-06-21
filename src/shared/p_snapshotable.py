from typing import Any, Protocol, Self


class PSnapshotable(Protocol):
    def snapshot(self) -> dict[str, Any]: ...
    
    @classmethod
    def from_snapshot(cls, snapshot: dict[str, Any]) -> Self: ...