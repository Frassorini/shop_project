import sqlite3
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Self

from sqlalchemy import StaticPool, event, text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Mapper

from shop_project.infrastructure.env_loader import get_env
from shop_project.infrastructure.persistence.repositories import init_repositories

init_repositories.init_repositories()


def _index_object(session: AsyncSession, instance: Any):
    set_ = session.info.get("strong_set", None)
    if not set_:
        session.info["strong_set"] = set_ = set()

    set_.add(instance)  # type: ignore


@event.listens_for(Mapper, "load")
def object_loaded(instance: Any, ctx: Any):
    _index_object(ctx.session, instance)


@event.listens_for(AsyncSession.sync_session_class, "after_attach")
def index_object(session: AsyncSession, instance: Any):
    _index_object(session, instance)


class Database:
    debug = False

    def __init__(self, db_url: str, echo: bool = False) -> None:
        self._engine = create_async_engine(db_url, echo=self.debug, future=True)
        self._session_factory = async_sessionmaker(
            bind=self._engine, expire_on_commit=False, class_=AsyncSession
        )

    @classmethod
    def from_engine(cls, engine: AsyncEngine) -> Self:
        obj = cls.__new__(cls)
        obj._engine = engine
        obj._session_factory = async_sessionmaker(
            bind=engine, expire_on_commit=False, class_=AsyncSession
        )

        return obj

    @classmethod
    def get_url_from_env(cls) -> str:
        return URL.create(
            drivername=get_env("DB_DRIVER"),
            username=get_env("DB_USER"),
            password=get_env("DB_PASSWORD"),
            host=get_env("DB_HOST"),
            port=int(get_env("DB_PORT")),
            database=get_env("DB_NAME"),
        ).render_as_string(hide_password=False)

    @classmethod
    def from_env(cls) -> Self:
        obj = cls.__new__(cls)
        obj.__init__(cls.get_url_from_env())
        return obj

    @classmethod
    def from_sync_conn(cls, conn: sqlite3.Connection) -> Self:
        """Создает AsyncEngine поверх существующего sqlite3 соединения"""
        engine = create_async_engine(
            "sqlite+aiosqlite://",
            # StaticPool гарантирует, что будет использовано ровно это соединение
            poolclass=StaticPool,
            # Если SQLAlchemy/aiosqlite будут требовать check_same_thread — лучше указать его при создании conn.
            connect_args={"check_same_thread": False},
            creator=lambda: conn,
            future=True,
            echo=cls.debug,
        )
        return cls.from_engine(engine)

    @asynccontextmanager
    async def session(
        self, lock_wait_timeout_ms: int
    ) -> AsyncGenerator[AsyncSession, None]:
        """Асинхронный контекстный менеджер для работы с сессией"""
        session_instance = self._session_factory()
        try:
            await self._apply_lock_timeout(session_instance, lock_wait_timeout_ms)
            yield session_instance
        finally:
            await session_instance.close()

    async def _apply_lock_timeout(
        self,
        session: AsyncSession,
        timeout_ms: int,
    ) -> None:
        dialect = session.bind.dialect.name

        if dialect == "mysql":
            # MySQL принимает секунды (int >= 1)
            timeout_seconds = max(1, timeout_ms // 1000)

            await session.execute(
                text("SET SESSION innodb_lock_wait_timeout = :timeout"),
                {"timeout": timeout_seconds},
            )

        elif dialect == "sqlite":
            await session.execute(
                text(f"PRAGMA busy_timeout = {int(timeout_ms)}")
            )  # sqlite doesn't support locks, but let this be just in case

    def get_engine(self) -> AsyncEngine:
        return self._engine

    def create_session(self) -> AsyncSession:
        return self._session_factory()

    async def close(self) -> None:
        await self._engine.dispose()
