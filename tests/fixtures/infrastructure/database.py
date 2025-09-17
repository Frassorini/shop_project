import sqlite3
from typing import AsyncGenerator, Callable, Coroutine, Literal, Type

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.database import models
from shop_project.infrastructure.unit_of_work import UnitOfWork


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[Database, None]:
    db = Database.from_env()

    async with db.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    yield db

    async with db.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)

    await db.engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def base_db_in_memory() -> sqlite3.Connection:
    """Создаём синхронную sqlite3 базу в памяти с таблицами"""
    sqlite_conn = sqlite3.connect(":memory:", check_same_thread=False)
    # Создаем таблицы через SQLAlchemy синхронно
    db = Database.from_sync_conn(sqlite_conn)
    async with db.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    return sqlite_conn


@pytest_asyncio.fixture
async def test_db_in_memory(base_db_in_memory: sqlite3.Connection) -> AsyncGenerator[Database, None]:
    """Клонируем базу для каждого теста"""
    clone_conn = sqlite3.connect(":memory:", check_same_thread=False)
    base_db_in_memory.backup(clone_conn)
    db = Database.from_sync_conn(clone_conn)
    try:
        yield db
    finally:
        await db.engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def fill_database(uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork]) -> Callable[[Database, dict[Type[BaseAggregate], list[BaseAggregate]]], Coroutine[None, None, Database]]:
    async def _fill_db(database: Database, data: dict[Type[BaseAggregate], list[BaseAggregate]]) -> Database:
        session = database.get_session()
        uow = uow_factory(session, 'read_write')
        async with uow:
            for model_type, domain_objects in data.items():
                uow.get_resorces().put_many(model_type, domain_objects)
            await uow.commit()
        return database
    return _fill_db