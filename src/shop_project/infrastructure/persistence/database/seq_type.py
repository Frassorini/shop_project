from sqlalchemy import BigInteger, Integer
from sqlalchemy.types import TypeDecorator


class SeqType(TypeDecorator[int]):
    """
    Диалектозависимый тип для seq:
    - SQLite: INTEGER PK autoincrement
    - Postgres/MySQL: BIGINT PK autoincrement
    """

    cache_ok = True

    impl = BigInteger  # базовый тип

    def load_dialect_impl(self, dialect):
        if dialect.name == "sqlite":
            return dialect.type_descriptor(Integer())
        else:
            return dialect.type_descriptor(BigInteger())
