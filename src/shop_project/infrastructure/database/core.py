from typing import Self

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy.engine import URL

from shop_project.env_loader import get_env


class Database:
    def __init__(self, db_url: str, echo: bool = True) -> None:
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
    def from_env(cls) -> Self:
        obj = cls.__new__(cls)
        url = URL.create(
            drivername="postgresql+asyncpg",
            username=get_env("POSTGRES_USER"),
            password=get_env("POSTGRES_PASSWORD"),
            host=get_env("POSTGRES_HOST"),
            port=int(get_env("POSTGRES_PORT")),
            database=get_env("POSTGRES_DB")
        )
        obj.__init__(url.render_as_string(hide_password=False))
        return obj

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    def get_session(self) -> AsyncSession:
        return self._session_factory()
