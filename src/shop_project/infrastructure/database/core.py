import sqlite3
from typing import Self

from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy.engine import URL
import aiosqlite

from shop_project.env_loader import get_env


class Database:
    def __init__(self, db_url: str, echo: bool = False) -> None:
        self._engine = create_async_engine(
            db_url,
            echo=echo,
            future=True
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
    
    @classmethod
    def from_engine(cls, engine: AsyncEngine) -> Self:
        obj = cls.__new__(cls)
        obj._engine = engine
        obj._session_factory = async_sessionmaker(
            bind=engine, 
            expire_on_commit=False, 
            class_=AsyncSession)
        
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

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    def get_session(self) -> AsyncSession:
        return self._session_factory()
