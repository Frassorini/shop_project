from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import AsyncIterator, Callable, TypeVar

T = TypeVar("T")


def create_context_from_value(value: T) -> Callable[[], AbstractAsyncContextManager[T]]:
    @asynccontextmanager
    async def _inner() -> AsyncIterator[T]:
        yield value

    return _inner
