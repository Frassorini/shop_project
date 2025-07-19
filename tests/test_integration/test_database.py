from typing import AsyncGenerator, Generator
import pytest
from sqlalchemy import select

from shop_project.infrastructure.database.core import Database


@pytest.mark.asyncio
@pytest.mark.integration
async def test_database(test_db: Database) -> None:
    session = test_db.get_session()
    await session.execute(select(1))
    await session.close()
    