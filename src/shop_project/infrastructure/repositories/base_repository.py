from abc import ABC
from typing import Any, Callable, Generic, Literal, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from plum import overload, dispatch

from shop_project import domain
from shop_project.application.dto.base_dto import BaseDTO
from shop_project.application.dto.mapper import to_domain, to_dto
from shop_project.domain.base_aggregate import BaseAggregate

from shop_project.infrastructure.query.base_load_query import BaseLoadQuery
from shop_project.infrastructure.query.prebuilt_load_query import PrebuiltLoadQuery
from shop_project.infrastructure.query.queries.load_query_translator import translate
from shop_project.infrastructure.query.domain_load_query import DomainLoadQuery
from shop_project.infrastructure.query.query_criteria import QueryCriteriaOperator, QueryCriterion, QueryCriteria, QueryCriterionOperator
from shop_project.shared.entity_id import EntityId


T = TypeVar('T', bound=BaseAggregate)


class BaseRepository(Generic[T], ABC):    
    model_type: Type[T]
    dto_type: Type[BaseDTO]
    
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def create(self, items: list[T]) -> None:
        ...

    async def update(self, items: list[T]) -> None:
        ...

    async def delete(self, items: list[T]) -> None:
        ...

    async def load(self, query: BaseLoadQuery) -> list[T]:
        result = await self.session.execute(translate(query))
        result = result.scalars().all()
        return [self.model_type.from_dict(self.dto_type.model_validate(item).model_dump()) for item in result]
    
    async def load_scalars(self, query: BaseLoadQuery) -> Any:
        result = await self.session.execute(translate(query))
        return result.scalars().all()

    async def save(self, difference_snapshot: dict[Literal['CREATED', 'UPDATED', 'DELETED'], list[BaseDTO]]) -> None:
        await self.create([to_domain(item) for item in difference_snapshot['CREATED']]) # type: ignore

        await self.update([to_domain(item) for item in difference_snapshot['UPDATED']]) # type: ignore

        await self.delete([to_domain(item) for item in difference_snapshot['DELETED']]) # type: ignore