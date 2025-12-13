import sqlite3
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Self

from sqlalchemy import StaticPool, event
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Mapper

from shop_project.infrastructure.env_loader import get_env
from shop_project.infrastructure.repositories import init_repositories

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
    def __init__(self, db_url: str, echo: bool = False) -> None:
        self._engine = create_async_engine(db_url, echo=echo, future=True)
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
    def from_env(cls) -> Self:
        obj = cls.__new__(cls)
        url = URL.create(
            drivername=get_env("DB_DRIVER"),
            username=get_env("DB_USER"),
            password=get_env("DB_PASSWORD"),
            host=get_env("DB_HOST"),
            port=int(get_env("DB_PORT")),
            database=get_env("DB_NAME"),
        )
        obj.__init__(url.render_as_string(hide_password=False))
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
            echo=False,
        )
        return cls.from_engine(engine)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Асинхронный контекстный менеджер для работы с сессией"""
        session_instance = self._session_factory()
        try:
            yield session_instance
        finally:
            await session_instance.close()

    def get_engine(self) -> AsyncEngine:
        return self._engine

    def create_session(self) -> AsyncSession:
        return self._session_factory()

    async def close(self) -> None:
        await self._engine.dispose()
