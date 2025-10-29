import asyncio
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from re import A
import sqlite3
from typing import Any, AsyncGenerator, Awaitable, Callable, Coroutine, Generator, Literal, Type

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import close_all_sessions

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.database import models
from shop_project.infrastructure.unit_of_work import UnitOfWork


@pytest_asyncio.fixture
async def test_db(request: pytest.FixtureRequest,
                  test_db_in_memory: Callable[[], AbstractAsyncContextManager[Database, None]],
                  test_db_docker: Callable[[], AbstractAsyncContextManager[Database, None]]
                  ) -> AsyncGenerator[Database, None]:
    if request.config.getoption("--real-db"):
        async with test_db_docker() as db:
            yield db
    else:
        async with test_db_in_memory() as db:
            yield db


@pytest.fixture(scope="function")
def test_db_docker() -> Callable[[], Any]:
    @asynccontextmanager
    async def fact() -> AsyncGenerator[Database, None]:
        db = Database.from_env()

        async with db.engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
            # await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            # await conn.commit()

        try:
            yield db

        finally:
            async with db.engine.begin() as conn:
                await conn.run_sync(models.Base.metadata.drop_all)
            await db.engine.dispose()
    return fact


@pytest.fixture
def base_db_in_memory() -> Callable[[], Awaitable[sqlite3.Connection]]:
    value: sqlite3.Connection | None = None
    
    async def fact() -> sqlite3.Connection:
        nonlocal value
        if value is not None:
            return value
        sqlite_conn = sqlite3.connect(":memory:", check_same_thread=False)
        db = Database.from_sync_conn(sqlite_conn)
        async with db.engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        value = sqlite_conn
        return sqlite_conn

    return fact


@pytest.fixture
def test_db_in_memory(base_db_in_memory: Callable[[], Awaitable[sqlite3.Connection]]) -> Callable[[], Any]:
    @asynccontextmanager
    async def fact() -> AsyncGenerator[Database, None]:
        clone_conn = sqlite3.connect(":memory:", check_same_thread=False)
        clone_conn.execute("PRAGMA foreign_keys = ON;")
        base_db = await base_db_in_memory()
        base_db.backup(clone_conn)
        db = Database.from_sync_conn(clone_conn)

        async with db.engine.begin() as conn:
            fk_list = await conn.run_sync(
                lambda sync_conn: sync_conn.execute(
                    text("PRAGMA foreign_key_list('purchase_active');")
                ).fetchall()
            )

            # print(f"{fk_list=}")
            assert len(fk_list) == 1
            fk = fk_list[0]

        try:
            yield db
        finally:
            await db.engine.dispose()

    return fact


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