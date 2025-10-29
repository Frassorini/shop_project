from typing import Any, Literal
from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.exceptions import UnitOfWorkException
from shop_project.infrastructure.query.base_load_query import BaseLoadQuery
from shop_project.infrastructure.query.domain_load_query import DomainLoadQuery
from shop_project.infrastructure.query.prebuilt_load_query import PrebuiltLoadQuery
from shop_project.infrastructure.query.query_plan import QueryPlan, LockQueryPlan, NoLockQueryPlan
from shop_project.infrastructure.resource_manager.resource_container import ResourceContainer
from shop_project.infrastructure.repositories.repository_container import RepositoryContainer
from shop_project.infrastructure.resource_manager.total_order_registry import TotalOrderRegistry
from shop_project.shared.entity_id import EntityId


class ResourceManager:
    def __init__(self, repository_container: RepositoryContainer, *, read_only: bool, raise_on_not_found: bool = True) -> None:
        self.repository_container = repository_container
        self.raise_on_not_found = raise_on_not_found
        self.read_only = read_only
        self.resource_container: ResourceContainer = ResourceContainer()
        if read_only:
            self.query_plan: QueryPlan = NoLockQueryPlan()
        else:
            self.query_plan: QueryPlan = LockQueryPlan()

    async def _load_single(self, query: BaseLoadQuery) -> None:
        if isinstance(query, PrebuiltLoadQuery) and query.return_type == 'SCALARS':
            loaded: Any = await self.repository_container.load_scalars(query)
        else:
            loaded: list[BaseAggregate] = await self.repository_container.load(query)
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
        
        ordered_types = TotalOrderRegistry.backward()
        sorted_diff = {
            model: difference[model]
            for model in ordered_types
            if model in difference
        }
        
        await self.repository_container.save(sorted_diff)
    
    def get_unique_id(self, model_type: type[BaseAggregate]) -> EntityId:
        return self.repository_container.get_unique_id(model_type)
