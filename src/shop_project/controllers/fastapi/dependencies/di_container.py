from typing import AsyncGenerator

from dishka.async_container import AsyncContainer
from fastapi import Request


async def get_container(request: Request) -> AsyncGenerator[AsyncContainer, None]:
    if not getattr(request.app.state, "container", None):
        raise RuntimeError("Container is not initialized")
    container: AsyncContainer = request.app.state.container

    async with container() as ctx:
        yield ctx
