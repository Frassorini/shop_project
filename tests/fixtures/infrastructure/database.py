from typing import AsyncGenerator

import pytest
import pytest_asyncio

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.database import models



@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[Database, None]:
    db = Database.from_env()

    async with db.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    yield db

    async with db.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)

    await db.engine.dispose()

