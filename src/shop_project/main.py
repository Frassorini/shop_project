from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.applications import Starlette

from dishka.container import Container
from shop_project.infrastructure.dependency_injection.infrastructure.container import InfrastructureContainer

@asynccontextmanager
async def lifespan(app: FastAPI):
    pass

    yield
    
    pass


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.container: Container = container
    return app