from contextlib import asynccontextmanager
from typing import AsyncGenerator, Awaitable, Callable, Optional, Self, TypeVar, Generic

T = TypeVar("T")

class AsyncLazyResource(Generic[T]):
    def __init__(self, factory: Callable[[], Awaitable[T]], disposer: Optional[Callable[[T], Awaitable[None]]] = None):
        self._factory = factory
        self._disposer = disposer
        self._instance: Optional[T] = None

    async def get(self) -> T:
        if self._instance is None:
            self._instance = await self._factory()
        return self._instance

    async def dispose(self) -> None:
        if self._instance is not None and self._disposer:
            await self._disposer(self._instance)
        self._instance = None

    async def __aenter__(self)  -> Self:
        return self

    async def __aexit__(self, exc_type: Optional[type], exc: Optional[object], tb: Optional[object]) -> None:
        await self.dispose()
