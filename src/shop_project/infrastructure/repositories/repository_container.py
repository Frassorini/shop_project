from typing import Any, Literal, Mapping, Type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.application.dto.base_dto import BaseDTO
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class RepositoryContainer:
    def __init__(
        self,
        repositories: dict[
            Type[PersistableEntity], BaseRepository[PersistableEntity, BaseDTO]
        ],
    ) -> None:
        self.repositories: dict[
            Type[PersistableEntity], BaseRepository[PersistableEntity, BaseDTO]
        ] = repositories

    async def load_scalars(self, query: CustomQuery) -> Any:
        return await self.repositories[query.model_type].load_scalars(query)

    async def load(self, query: BaseQuery) -> list[PersistableEntity]:
        return await self.repositories[query.model_type].load(query)

    async def save(
        self,
        resource_changes_snapshot: dict[
            Type[PersistableEntity],
            dict[Literal["CREATED", "UPDATED", "DELETED"], list[BaseDTO]],
        ],
    ) -> None:
        for entity_type, difference in resource_changes_snapshot.items():
            await self.repositories[entity_type].save(difference)

    def get_unique_id(self, model_type: type[PersistableEntity]) -> UUID:
        raise NotImplementedError


def repository_container_factory(
    session: AsyncSession,
    repositories: Mapping[Type[PersistableEntity], Type[BaseRepository[Any, Any]]],
) -> RepositoryContainer:
    return RepositoryContainer(
        {
            model_type: repository(session)
            for model_type, repository in repositories.items()
        }
    )
