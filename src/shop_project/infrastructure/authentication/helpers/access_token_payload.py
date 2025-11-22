from dataclasses import dataclass
from enum import Enum
from typing import Any, Self

from shop_project.shared.entity_id import EntityId


class SessionType(Enum):
    CUSTOMER = "CUSTOMER"
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"


@dataclass(frozen=True)
class AccessTokenPayload:
    session_type: SessionType
    subject_id: EntityId

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_type": self.session_type.value,
            "subject_id": self.subject_id.value,
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        return cls(
            session_type=SessionType(snapshot["session_type"]),
            subject_id=EntityId(snapshot["subject_id"]),
        )
