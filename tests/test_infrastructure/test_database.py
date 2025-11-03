from typing import AsyncGenerator, Awaitable, Callable, Generator
import sqlite3
from sqlite3.dbapi2 import IntegrityError

import pytest
import pytest_asyncio
from sqlalchemy import select

from shop_project.infrastructure.database.core import Database


@pytest.mark.asyncio
@pytest.mark.integration
async def test_database(test_db: Database) -> None:
    session = test_db.create_session()
    await session.execute(select(1))
    await session.close()


@pytest.mark.asyncio
async def test_foreign_key_delete_violation(base_db_in_memory: Callable[[], Awaitable[sqlite3.Connection]]):
    # Создаём клон in-memory базы
    clone_conn = sqlite3.connect(":memory:", check_same_thread=False)
    
    base_conn = await base_db_in_memory()
    base_conn.backup(clone_conn)

    # Включаем проверки внешних ключей
    clone_conn.execute("PRAGMA foreign_keys = ON;")

    # Создаём таблицы с FK
    clone_conn.execute("CREATE TABLE parent(id INTEGER PRIMARY KEY)")
    clone_conn.execute("""
        CREATE TABLE child(
            id INTEGER PRIMARY KEY,
            parent_id INTEGER,
            FOREIGN KEY(parent_id) REFERENCES parent(id)
        )
    """)
    clone_conn.commit()

    # Вставляем корректные данные
    clone_conn.execute("INSERT INTO parent(id) VALUES (1)")
    clone_conn.execute("INSERT INTO child(id, parent_id) VALUES (1, 1)")
    clone_conn.commit()

    # Попытка удалить родителя, на которого ссылается child
    with pytest.raises(IntegrityError) as excinfo:
        clone_conn.execute("DELETE FROM parent WHERE id = 1")

    assert "FOREIGN KEY constraint failed" in str(excinfo.value)
    clone_conn.close()


@pytest.mark.asyncio
async def test_clone_isolation(base_db_in_memory: Callable[[], Awaitable[sqlite3.Connection]]):
    clone_conn_1 = sqlite3.connect(":memory:", check_same_thread=False)
    (await base_db_in_memory()).backup(clone_conn_1)
    clone_conn_2 = sqlite3.connect(":memory:", check_same_thread=False)
    (await base_db_in_memory()).backup(clone_conn_2)
    
    clone_conn_1.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY)")
    clone_conn_1.commit()
    
    cur_clone_1 = clone_conn_1.cursor()
    cur_clone_1.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'"
    )
    assert cur_clone_1.fetchone() is not None, "Таблица не создалась!"
    cur_base = (await base_db_in_memory()).cursor()
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