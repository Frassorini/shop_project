from domain.p_aggregate import PAggregate
from infrastructure.exceptions import UnitOfWorkException
from infrastructure.query.load_query import LoadQuery
from infrastructure.resource_manager.resource_container import ResourceContainer
from infrastructure.repositories.repository_container import RepositoryContainer


class ResourceManager:
    def __init__(self, repository_container: RepositoryContainer, raise_on_not_found: bool = True) -> None:
        self.repository_container = repository_container
        self.raise_on_not_found = raise_on_not_found
        self.resource_container: ResourceContainer = ResourceContainer()

    def _load_single(self, query: LoadQuery) -> None:     
        loaded: list[PAggregate] = self.repository_container\
            .get_by_attribute(query.model_type, 
                                      query.attribute_provider.attribute_name, 
                                      query.attribute_provider.get())
        
        self.resource_container.put_many(query.model_type, loaded)
        
        loaded_ids = [item.entity_id for item in loaded]
        
        for entity_id in query.attribute_provider.get():
            if entity_id not in loaded_ids and self.raise_on_not_found:
                raise UnitOfWorkException(f"Could not find {query.model_type} with id {entity_id}")
        
        query.result = loaded
        query.is_loaded = True

    def load(self, queries: list[LoadQuery]) -> ResourceContainer:
        for query in queries:
            self._load_single(query)
        
        return self.resource_container
    
    def save(self) -> None:
        self.resource_container.take_snapshot()
        
        difference = self.resource_container.get_resource_changes()
        
        self.repository_container.save(difference)