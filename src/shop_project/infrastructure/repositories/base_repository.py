from abc import ABC
from typing import Any, Callable, Generic, Literal, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from plum import overload, dispatch
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import select, delete, insert, update, case, and_
from sqlalchemy import bindparam

from shop_project import domain
from shop_project.application.dto.base_dto import BaseDTO
from shop_project.application.dto.mapper import to_domain, to_dto
from shop_project.domain.persistable_entity import PersistableEntity

from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.query.queries.sqlalchemy_query_compiler import compile_query
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.query_criteria import QueryCriteriaOperator, QueryCriterion, QueryCriteria, QueryCriterionOperator
from shop_project.shared.entity_id import EntityId


T = TypeVar('T', bound=PersistableEntity)


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

    async def load(self, query: BaseQuery) -> list[T]:
        result = await self.session.execute(compile_query(query))
        result = result.scalars().unique().all()
        return [self.model_type.from_dict(self.dto_type.model_validate(item).model_dump()) for item in result]
    
    async def load_scalars(self, query: BaseQuery) -> Any:
        result = await self.session.execute(compile_query(query))
        return result.scalars().unique().all()

    async def save(self, difference_snapshot: dict[Literal['CREATED', 'UPDATED', 'DELETED'], list[BaseDTO]]) -> None:
        await self.create([to_domain(item) for item in difference_snapshot['CREATED']]) # type: ignore

        await self.update([to_domain(item) for item in difference_snapshot['UPDATED']]) # type: ignore

        await self.delete([to_domain(item) for item in difference_snapshot['DELETED']]) # type: ignore

    @staticmethod
    async def _replace_children(
        session: AsyncSession,
        root_id_name: str,
        root_ids: list[Any],
        child_model: type,
        new_items: list[dict[str, Any]],
    ) -> None:
        """
        Полностью заменяет дочерние записи для указанных root_id.

        :param session: Асинхронная сессия SQLAlchemy
        :param root_id_name: Имя колонки внешнего ключа в дочерней таблице
        :param root_ids: Список ID root-объектов, для которых меняем дочерние элементы
        :param child_model: ORM-модель дочерней таблицы
        :param new_items: Список новых дочерних записей (dict), уже с root_id
        """
        if not root_ids:
            return

        # 1. Удаляем старые записи
        await session.execute(delete(child_model).where(
            getattr(child_model, root_id_name).in_(root_ids)
        ))

        # 2. Вставляем новые
        if new_items:
            await session.execute(insert(child_model), new_items)

    @staticmethod
    def _build_bulk_update_case(
        field_name: str,
        snapshots: list[dict[str, Any]],
        model_cls: type,
        pk_fields: list[str],
    ) -> Any:
        """
        Создаёт SQLAlchemy CASE для массового обновления одного поля, поддерживает составной PK.
        :param field_name: Название обновляемого поля.
        :param snapshots: Список dict'ов, каждый содержит значения всех ключевых полей и обновляемых полей.
        :param model_cls: ORM-модель.
        :param pk_fields: Список названий колонок, которые составляют первичный ключ.
        """
        column: InstrumentedAttribute[Any] = getattr(model_cls, field_name)
        return case(
            *(
                (
                    and_(*(getattr(model_cls, pk) == snap[pk] for pk in pk_fields)),
                    bindparam(
                        f"{field_name}_{idx}",
                        snap[field_name],
                        type_=column.type,
                    ),
                )
                for idx, snap in enumerate(snapshots)
            )
        )