from contextlib import asynccontextmanager

from dishka.async_container import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from shop_project.controllers.fastapi.exception_handling.handlers import (
    register_exception_handlers,
)
from shop_project.controllers.fastapi.routers.auth import router as auth_router
from shop_project.controllers.fastapi.routers.customer import router as customer_router
from shop_project.controllers.fastapi.routers.employee import router as employee_router
from shop_project.controllers.fastapi.routers.manager import router as manager_router
from shop_project.controllers.fastapi.routers.shared import router as shared_router
from shop_project.infrastructure.dependency_injection.factories import (
    container_fastapi_factory,
)
from shop_project.infrastructure.env_loader import get_env


@asynccontextmanager
async def lifespan(app: FastAPI):
    pass

    yield

    if app.state.container is not None:
        await app.state.container.close()

    pass


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    container: AsyncContainer = container_fastapi_factory()

    setup_dishka(container, app)
    app.state.container = container

    register_exception_handlers(app)

    app.include_router(shared_router)
    app.include_router(customer_router)
    app.include_router(employee_router)
    app.include_router(manager_router)
    app.include_router(auth_router)

    if get_env("WITH_TEST_ROUTER"):
        from shop_project.controllers.fastapi.routers.testing import (
            router as test_router,
        )

        app.include_router(test_router)

    return app
