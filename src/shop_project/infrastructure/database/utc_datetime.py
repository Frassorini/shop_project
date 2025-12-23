import datetime

from sqlalchemy.types import BigInteger, DateTime, TypeDecorator


class UTCDateTime(TypeDecorator[datetime.datetime]):
    """
    Хранение времени в UTC.
    В sqlite — как BIGINT (timestamp).
    В других диалектах — обычный DATETIME.
    """

    cache_ok = True

    # базовый тип по умолчанию
    impl = DateTime

    def load_dialect_impl(self, dialect):
        if dialect.name == "sqlite":
            # Для sqlite используем BIGINT
            return dialect.type_descriptor(BigInteger())
        return dialect.type_descriptor(DateTime())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.timezone.utc)
        value = value.astimezone(datetime.timezone.utc)

        if dialect.name == "sqlite":
            # sqlite хранит как Unix timestamp
            return int(value.timestamp())
        else:
            # другие диалекты получают naive datetime
            return value.replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        if dialect.name == "sqlite":
            return datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
        else:
            return value.replace(tzinfo=datetime.timezone.utc)
