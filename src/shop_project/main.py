from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dishka import make_async_container
from dishka.async_container import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.dependency_injection.domain.domain_provider import (
    DomainProvider,
)
from shop_project.infrastructure.dependency_injection.infrastructure.database_provider import (
    DatabaseProvider,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    pass

    yield

    pass


@asynccontextmanager
async def database_ctx() -> AsyncGenerator[Database, None]:
    db = Database.from_env()
    try:
        yield db
    finally:
        await db.close()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    container: AsyncContainer = make_async_container(
        DomainProvider(), DatabaseProvider(database_ctx)
    )

    setup_dishka(container, app)
    return app
