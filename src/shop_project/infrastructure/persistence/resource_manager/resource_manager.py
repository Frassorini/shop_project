from typing import Any, Type
from uuid import UUID

from shop_project.application.shared.base_dto import BaseDTO
from shop_project.application.shared.dto.mapper import to_domain
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.exceptions import UnitOfWorkException
from shop_project.infrastructure.persistence.query.base_query import BaseQuery
from shop_project.infrastructure.persistence.query.custom_query import CustomQuery
from shop_project.infrastructure.persistence.query.query_plan import (
    LockQueryPlan,
    NoLockQueryPlan,
    QueryPlan,
)
from shop_project.infrastructure.persistence.repositories.repository_container import (
    RepositoryContainer,
)
from shop_project.infrastructure.persistence.resource_manager.resource_container import (
    ResourceContainer,
)
from shop_project.infrastructure.registries.total_order_registry import (
    TotalOrderRegistry,
)


class ResourceManager:
    def __init__(
        self,
        repository_container: RepositoryContainer,
        total_order: Type[TotalOrderRegistry],
        *,
        resources_registry: list[Type[PersistableEntity]],
        read_only: bool,
    ) -> None:
        self.repository_container: RepositoryContainer = repository_container
        self.read_only: bool = read_only
        self.total_order: Type[TotalOrderRegistry] = total_order
        self.resource_container: ResourceContainer = ResourceContainer(
            resources_registry
        )
        if read_only:
            self.query_plan: QueryPlan = NoLockQueryPlan()
        else:
            self.query_plan: QueryPlan = LockQueryPlan()

    async def _load_single(self, query: BaseQuery) -> None:
        if isinstance(query, CustomQuery) and query.return_type == "SCALARS":
            loaded: Any = await self.repository_container.load_scalars(query)
        else:
            loaded_dto: list[BaseDTO[Any]] = await self.repository_container.load(query)
            loaded: list[PersistableEntity] = [to_domain(dto) for dto in loaded_dto]

            self.resource_container.put_many(query.model_type, loaded)

        query.load(loaded)

    async def load(self, query_plan: QueryPlan) -> ResourceContainer:
        for query in query_plan.queries:
            await self._load_single(query)

        if self.read_only != query_plan.read_only:
            raise UnitOfWorkException("Invalid query plan read only state")

        self.query_plan = query_plan

        return self.resource_container

    async def save(self) -> None:
        self.resource_container.take_snapshot()

        difference = self.resource_container.get_resource_changes()

        self.query_plan.validate_changes(difference)

        ordered_types = self.total_order.backward()
        sorted_diff = {
            model: difference[model] for model in ordered_types if model in difference
        }

        await self.repository_container.save(sorted_diff)

    def get_unique_id(self, model_type: type[PersistableEntity]) -> UUID:
        return self.repository_container.get_unique_id(model_type)
