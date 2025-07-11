from typing import Any, Literal
from domain.p_aggregate import PAggregate
from infrastructure.exceptions import UnitOfWorkException
from infrastructure.query.load_query import LoadQuery
from infrastructure.query.query_plan import QueryPlan, LockQueryPlan, NoLockQueryPlan
from infrastructure.resource_manager.resource_container import ResourceContainer
from infrastructure.repositories.repository_container import RepositoryContainer


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

    def _load_single(self, query: LoadQuery) -> None:
        loaded: list[PAggregate] = self.repository_container.load_from_query(query)
        
        self.resource_container.put_many(query.model_type, loaded)

        query.load(loaded)

    def load(self, query_plan: QueryPlan) -> ResourceContainer:
        for query in query_plan.queries:
            self._load_single(query)
        
        if self.read_only != query_plan.read_only:
            raise UnitOfWorkException("Invalid query plan read only state")
        
        self.query_plan = query_plan
        
        return self.resource_container
    
    def save(self) -> None:
        self.resource_container.take_snapshot()
        
        difference = self.resource_container.get_resource_changes()
        
        self.query_plan.validate_changes(difference)
        
        self.repository_container.save(difference)
    
    # def validate_save(self, queries: list[LoadQuery], difference: dict[Literal['CREATED', 'UPDATED', 'DELETED'], list[dict[str, Any]]]) -> None:
        