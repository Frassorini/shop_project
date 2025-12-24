from uuid import UUID

from sqlalchemy.types import BINARY, TypeDecorator


class UUIDBinary(TypeDecorator[UUID]):
    """
    Кастомный тип для SQLAlchemy:
    - В Python всегда uuid.UUID
    - В MySQL хранится как BINARY(16)
    """

    impl = BINARY(16)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Python → БД"""
        if value is None:
            return None
        if isinstance(value, UUID):
            return value.bytes
        raise TypeError(f"Expected uuid.UUID, got {type(value).__name__}")

    def process_result_value(self, value, dialect):
        """БД → Python"""
        if value is None:
            return None
        return UUID(bytes=value)
