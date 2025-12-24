import sqlite3
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any, AsyncGenerator, Callable

import pytest
import pytest_asyncio
from dishka import AsyncContainer

from shop_project.infrastructure.persistence.database.core import Database
from shop_project.infrastructure.persistence.database.models.base import Base


@pytest_asyncio.fixture
async def test_db(
    async_container: AsyncContainer,
) -> AsyncGenerator[Database, None]:
    yield await async_container.get(Database)


@pytest.fixture
def test_db_factory(
    request: pytest.FixtureRequest,
    test_db_in_memory: Callable[[], AbstractAsyncContextManager[Database, None]],
    test_db_docker: Callable[[], AbstractAsyncContextManager[Database, None]],
) -> Callable[[], AbstractAsyncContextManager[Database, None]]:
    if request.config.getoption("--real-db"):
        return test_db_docker
    else:
        return test_db_in_memory


@pytest_asyncio.fixture(autouse=True, scope="session")
async def session_docker_db(
    request: pytest.FixtureRequest,
) -> AsyncGenerator[Database | None, None]:
    if not request.config.getoption("--real-db"):
        yield None
    else:
        db = Database.from_env()
        async with db.get_engine().begin() as conn:
            # Создаем схему один раз на всю сессию тестов
            await conn.run_sync(Base.metadata.create_all)
        yield db
        # Очистка схемы после всех тестов (опционально)
        async with db.get_engine().begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await db.close()


@pytest.fixture
def test_db_docker() -> Callable[[], AbstractAsyncContextManager[Database]]:
    @asynccontextmanager
    async def fact() -> AsyncGenerator[Database, None]:
        db = Database.from_env()
        async with db.get_engine().begin() as conn:
            # Очистка данных из всех таблиц перед тестом
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(table.delete())
        try:
            yield db
        finally:
            async with db.get_engine().begin() as conn:
                # Очистка данных после теста
                for table in reversed(Base.metadata.sorted_tables):
                    await conn.execute(table.delete())
            await db.close()

    return fact


@pytest_asyncio.fixture(scope="session")
async def base_db_in_memory() -> AsyncGenerator[sqlite3.Connection, None]:
    sqlite_conn = sqlite3.connect(":memory:", check_same_thread=False)
    db = Database.from_sync_conn(sqlite_conn)
    async with db.get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    value = sqlite_conn
    try:
        yield sqlite_conn
    finally:
        await db.close()
        value.close()


@pytest.fixture
def test_db_in_memory(base_db_in_memory: sqlite3.Connection) -> Callable[[], Any]:
    @asynccontextmanager
    async def fact() -> AsyncGenerator[Database, None]:
        clone_conn = sqlite3.connect(":memory:", check_same_thread=False)
        clone_conn.execute("PRAGMA foreign_keys = ON;")
        base_db_in_memory.backup(clone_conn)
        db = Database.from_sync_conn(clone_conn)

        try:
            yield db
        finally:
            await db.close()

    return fact
