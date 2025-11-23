from dataclasses import dataclass
from enum import Enum
from typing import Any, Self
from uuid import UUID


class SessionType(Enum):
    CUSTOMER = "CUSTOMER"
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"


@dataclass(frozen=True)
class AccessTokenPayload:
    session_type: SessionType
    subject_id: UUID

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_type": self.session_type.value,
            "subject_id": self.subject_id,
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        return cls(
            session_type=SessionType(snapshot["session_type"]),
            subject_id=snapshot["subject_id"],
        )
