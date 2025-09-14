from typing import AsyncGenerator, Generator
import sqlite3

import pytest
import pytest_asyncio
from sqlalchemy import select

from shop_project.infrastructure.database.core import Database


@pytest.mark.asyncio
@pytest.mark.integration
async def test_database(test_db: Database) -> None:
    session = test_db.get_session()
    await session.execute(select(1))
    await session.close()


@pytest.mark.asyncio
async def test_clone_isolation(base_db_in_memory: sqlite3.Connection):
    clone_conn_1 = sqlite3.connect(":memory:", check_same_thread=False)
    base_db_in_memory.backup(clone_conn_1)
    clone_conn_2 = sqlite3.connect(":memory:", check_same_thread=False)
    base_db_in_memory.backup(clone_conn_2)
    
    clone_conn_1.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY)")
    clone_conn_1.commit()
    
    cur_clone_1 = clone_conn_1.cursor()
    cur_clone_1.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'"
    )
    assert cur_clone_1.fetchone() is not None, "Таблица не создалась!"
    cur_base = base_db_in_memory.cursor()
    cur_base.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'"
    )
    assert cur_base.fetchone() is None, "Изменения клона утекли в базовую базу!"
    cur_clone_2 = clone_conn_2.cursor()
    cur_clone_2.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'"
    )
    assert cur_clone_2.fetchone() is None, "Изменения одного клона утекли в другой!"

    clone_conn_1.close()
    clone_conn_2.close()