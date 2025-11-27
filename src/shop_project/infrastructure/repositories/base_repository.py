from abc import ABC
from typing import Any, Generic, Literal, Type, TypeVar

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm._typing import _IdentityKeyType  # type: ignore

from shop_project.application.dto.base_dto import BaseDTO
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.database.models.base import Base as BaseORM
from shop_project.infrastructure.query.base_query import BaseQuery, QueryLock
from shop_project.infrastructure.query.custom_query import CustomQuery

E = TypeVar("E", bound=PersistableEntity)
D = TypeVar("D", bound=BaseDTO)
T = TypeVar("T", bound=BaseORM)


class BaseRepository(Generic[E, D], ABC):
    model_type: Type[E]
    dto_type: Type[D]

    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def create(self, items: list[D]) -> None: ...

    async def update(self, items: list[D]) -> None: ...

    async def delete(self, items: list[D]) -> None: ...

    async def load(self, query: BaseQuery) -> list[E]: ...

    async def load_scalars(self, query: CustomQuery) -> Any:
        result = await self.session.execute(query.compile_sqlalchemy())
        return result.scalars().unique().all()

    async def save(
        self,
        difference_snapshot: dict[
            Literal["CREATED", "UPDATED", "DELETED"], list[BaseDTO]
        ],
    ) -> None:
        await self.create(difference_snapshot["CREATED"])  # type: ignore

        await self.update(difference_snapshot["UPDATED"])  # type: ignore

        await self.delete(difference_snapshot["DELETED"])  # type: ignore

    @staticmethod
    def _apply_lock(query: Any, lock: QueryLock, of: list[Any]):
        if lock == QueryLock.EXCLUSIVE:
            return query.with_for_update(of=of)
        elif lock == QueryLock.SHARED:
            return query.with_for_update(read=True, of=of)
        return query

    @staticmethod
    def _get_identity_key(model_type: Type[T], *args: Any) -> _IdentityKeyType[T]:
        return inspect(model_type).identity_key_from_primary_key((*args,))
