from dataclasses import dataclass
from typing import Any, Self, cast
from uuid import UUID


@dataclass(frozen=True)
class EntityId:
    value: UUID

    def __post_init__(self):
        if not isinstance(self.value, UUID):
            raise TypeError(f"EntityId.value must be UUID, got {type(self.value).__name__}")

    def to_str(self) -> str:
        """Возвращает строковое представление UUID для хранения в БД"""
        return str(self.value)

    @classmethod
    def from_str(cls, raw: str) -> "EntityId":
        """Создаёт EntityId из строки (например, из БД)"""
        return cls(UUID(raw))