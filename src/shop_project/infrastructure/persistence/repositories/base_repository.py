from abc import ABC
from typing import Any, Generic, Literal, Mapping, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Select, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload
from sqlalchemy.orm._typing import _IdentityKeyType  # type: ignore
from sqlalchemy.sql import select

from shop_project.application.shared.base_dto import BaseDTO, BaseVODTO
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.persistence.database.models.base import Base as BaseORM
from shop_project.infrastructure.persistence.query.base_query import (
    BaseQuery,
    QueryLock,
)
from shop_project.infrastructure.persistence.query.composed_query import ComposedQuery
from shop_project.infrastructure.persistence.query.custom_query import CustomQuery
from shop_project.infrastructure.registries.resources_registry import ResourcesRegistry

BD = TypeVar("BD", bound=BaseDTO[Any])
BO = TypeVar("BO", bound=BaseORM)
PE = TypeVar("PE", bound=PersistableEntity)


class RepositoryRegistry:
    _registry: dict[Type[PersistableEntity], "Type[BaseRepository[Any, Any, Any]]"] = {}

    @classmethod
    def register(
        cls,
        resource_type: Type[PersistableEntity],
        repository_type: "Type[BaseRepository[Any, Any, Any]]",
    ) -> None:
        if resource_type in cls._registry:
            raise ValueError(f"Resource type {resource_type} already registered")

        cls._registry[resource_type] = repository_type

    @classmethod
    def get_map(
        cls,
    ) -> "Mapping[Type[PersistableEntity], Type[BaseRepository[Any, Any, Any]]]":
        return cls._registry


class ChildDescriptor(BaseModel):
    child_orm: Type[BaseORM]
    parent_dto_child_container_field_name: str
    child_dto_parent_reference_field_name: str
    child_dto_other_pk_field_names: list[str]


class BaseRepository(Generic[BO, BD, PE], ABC):
    orm_type: Type[BO]
    dto_type: Type[BD]
    entity_type: Type[PE]

    child_descriptors: list[ChildDescriptor]

    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    def _get_child_pk_tuple(
        self,
        parent_pk: UUID,
        child_dto: BaseORM | BaseVODTO,
        child_descriptor: ChildDescriptor,
    ) -> tuple[UUID, ...]:
        res: list[Any] = []

        other_pks: list[Any] = []
        for pk_name in child_descriptor.child_dto_other_pk_field_names:
            other_pks.append(getattr(child_dto, pk_name))

        res.append(parent_pk)
        res.extend(other_pks)
        return tuple(res)

    async def create(self, items: list[BD]) -> None:
        if not items:
            return

        for dto in items:
            entity: BO = self.orm_type(**dto.model_dump())

            entity_id_field = getattr(entity, "entity_id", None)
            if not entity_id_field:
                raise RuntimeError(
                    f"Parent entity {self.orm_type.__name__} has no entity_id field"
                )

            self.session.add(entity)

            for child_descriptor in self.child_descriptors:
                for child_dto in getattr(
                    dto, child_descriptor.parent_dto_child_container_field_name
                ):
                    child = child_descriptor.child_orm(
                        **child_dto.model_dump(),
                        **{
                            child_descriptor.child_dto_parent_reference_field_name: entity_id_field
                        },
                    )
                    setattr(
                        child,
                        child_descriptor.child_dto_parent_reference_field_name,
                        entity_id_field,
                    )
                    self.session.add(child)

    async def update(self, items: list[BD]) -> None:
        if not items:
            return

        for dto in items:
            entity = self.session.identity_map.get(
                self._get_identity_key(self.orm_type, dto.entity_id)
            )
            if not entity:
                continue

            entity_id_field = getattr(entity, "entity_id", None)
            if not entity_id_field:
                raise RuntimeError(
                    f"Parent entity {self.orm_type.__name__} has no entity_id field"
                )

            entity.repopulate(**dto.model_dump())

            for child_descriptor in self.child_descriptors:
                entity_children_container: list[BO] = getattr(
                    entity, child_descriptor.parent_dto_child_container_field_name
                )
                dto_children_container: list[BaseVODTO] = getattr(
                    dto, child_descriptor.parent_dto_child_container_field_name
                )

                current_children: dict[tuple[UUID, ...], BO] = {
                    self._get_child_pk_tuple(
                        entity_id_field, child, child_descriptor
                    ): child
                    for child in entity_children_container
                }

                for child in current_children.values():
                    await self.session.delete(child)

                for child_dto in dto_children_container:
                    key = self._get_child_pk_tuple(
                        entity_id_field, child_dto, child_descriptor
                    )
                    if key in current_children:
                        current_children[key].repopulate(
                            **child_dto.model_dump(),
                            **{
                                child_descriptor.child_dto_parent_reference_field_name: entity_id_field
                            },
                        )
                        self.session.add(current_children[key])
                    else:
                        child = child_descriptor.child_orm(
                            **child_dto.model_dump(),
                            **{
                                child_descriptor.child_dto_parent_reference_field_name: entity_id_field
                            },
                        )
                        setattr(
                            child,
                            child_descriptor.child_dto_parent_reference_field_name,
                            entity_id_field,
                        )
                        self.session.add(child)

    async def delete(self, items: list[BD]) -> None:
        if not items:
            return

        for dto in items:
            entity = self.session.identity_map.get(
                self._get_identity_key(self.orm_type, dto.entity_id)
            )

            if not entity:
                raise RuntimeError(
                    f"Entity of type {self.dto_type.__name__} {dto.entity_id} not found for deleting"
                )

            for child_descriptor in self.child_descriptors:
                entity_children_container: list[BaseORM] = getattr(
                    entity, child_descriptor.parent_dto_child_container_field_name
                )
                for child in list(entity_children_container):
                    await self.session.delete(child)

            await self.session.delete(entity)

    async def load(self, query: BaseQuery) -> list[BD]:
        if isinstance(query, ComposedQuery):
            aliases = {
                child_descriptor.parent_dto_child_container_field_name: aliased(
                    child_descriptor.child_orm,
                    name=child_descriptor.child_orm.__tablename__,
                )
                for child_descriptor in self.child_descriptors
            }

            child_tables: dict[str, type[BaseORM]] = {
                child_descriptor.parent_dto_child_container_field_name: child_descriptor.child_orm
                for child_descriptor in self.child_descriptors
            }

            parent_refs: dict[str, str] = {
                child_descriptor.parent_dto_child_container_field_name: child_descriptor.child_dto_parent_reference_field_name
                for child_descriptor in self.child_descriptors
            }

            base_query = select(self.orm_type)

            for child_descriptor in self.child_descriptors:
                alias = aliases[child_descriptor.parent_dto_child_container_field_name]
                children_container_field = getattr(
                    self.orm_type,
                    child_descriptor.parent_dto_child_container_field_name,
                )
                base_query = base_query.options(joinedload(children_container_field))

            base_query = base_query.where(
                query.criteria.to_sqlalchemy(
                    self.orm_type, child_tables=child_tables, parent_refs=parent_refs
                )
            )

            base_query = self._apply_lock_mysql(base_query, query.lock)
        elif isinstance(query, CustomQuery):
            base_query = query.compile_sqlalchemy()
        else:
            raise ValueError(f"Unknown query type: {type(query)}")

        result_raw = await self.session.execute(base_query)
        result_orm = result_raw.scalars().unique().all()
        result = [self.dto_type.model_validate(item) for item in result_orm]

        return result

    async def load_scalars(self, query: CustomQuery) -> Any:
        result = await self.session.execute(query.compile_sqlalchemy())
        return result.scalars().unique().all()

    async def save(
        self,
        difference_snapshot: dict[
            Literal["CREATED", "UPDATED", "DELETED"], list[BaseDTO[Any]]
        ],
    ) -> None:
        await self.create(difference_snapshot["CREATED"])  # type: ignore

        await self.update(difference_snapshot["UPDATED"])  # type: ignore

        await self.delete(difference_snapshot["DELETED"])  # type: ignore

    @staticmethod
    def _apply_lock_mysql(query: Select[Any], lock: QueryLock):
        if lock == QueryLock.EXCLUSIVE:
            return query.with_for_update()
        elif lock == QueryLock.EXCLUSIVE_NOWAIT:
            return query.with_for_update(nowait=True)
        elif lock == QueryLock.SHARED:
            return query.with_for_update(read=True)
        elif lock == QueryLock.SHARED_NOWAIT:
            return query.with_for_update(read=True, nowait=True)
        return query

    @staticmethod
    def _get_identity_key(model_type: Type[BO], *args: Any) -> _IdentityKeyType[BO]:
        return inspect(model_type).identity_key_from_primary_key((*args,))

    def __init_subclass__(cls):
        if cls.is_needed_to_register():
            if not hasattr(cls, "child_descriptors"):
                cls.child_descriptors = []
            orm_type, dto_type, entity_type = cls._get_generic_types()

            # print(orm_type, dto_type, entity_type)

            cls.orm_type = orm_type
            cls.dto_type = dto_type
            cls.entity_type = entity_type

            RepositoryRegistry.register(entity_type, cls)
            ResourcesRegistry.register(entity_type)

        return super().__init_subclass__()

    @classmethod
    def _get_generic_types(cls) -> tuple[Any, Any, Any]:
        bases = cls.__bases__
        for base in getattr(cls, "__orig_bases__", ()):
            args = getattr(base, "__args__", None)
            if not args:
                continue
            if not len(args) == 3:
                raise RuntimeError("Generic has not two types")
            type1_, type2_, type3_ = args
            if (
                isinstance(type1_, TypeVar)
                or isinstance(type2_, TypeVar)
                or isinstance(type3_, TypeVar)
            ):
                raise RuntimeError("Generic type is lost")
            return type1_, type2_, type3_
        raise RuntimeError("Generic type is not found in generic base")

    @classmethod
    def is_needed_to_register(cls) -> bool:
        bases = getattr(cls, "__orig_bases__", None)
        if not bases:
            raise RuntimeError("Generic metadata is not found")

        for base in bases:
            if getattr(base, "__args__", None):
                return True
        return False
