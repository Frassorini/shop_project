from typing import Any

from application.resource_loader.load_query import LoadQuery
from application.resource_loader.resource_container import ResourceContainer
from application.resource_loader.repository_container import RepositoryContainer


class ResourceManager:
    def __init__(self, repository_container: RepositoryContainer) -> None:
        self.repository_container = repository_container
        self.resources: ResourceContainer = ResourceContainer()

    def _load_single(self, query: LoadQuery) -> None:     
        loaded: list[Any] = self.repository_container\
            .get_by_attribute(query.model_type, 
                                      query.attribute_provider.attribute_name, 
                                      query.attribute_provider.get())
        self.resources.put_many(query.model_type, loaded)
        
        query.result = loaded
        query.is_loaded = True

    def load(self, queries: list[LoadQuery]) -> ResourceContainer:
        for query in queries:
            self._load_single(query)
        
        return self.resources