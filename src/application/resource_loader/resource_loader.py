from typing import Any, Type, TypeVar, cast

from shared.entity_id import EntityId

from application.resource_loader.load_query import LoadQuery

from application.interfaces.p_repository import PRepository

from domain.customer_order.model import CustomerOrder
from domain.store_item.model import StoreItem


ExtractedAttributeType = TypeVar('ExtractedAttributeType')
ModelType = TypeVar('ModelType', 
                    CustomerOrder, 
                    StoreItem,
                    )


class RepositoryContainer:
    def __init__(self, 
                 customer_order: PRepository[CustomerOrder],
                 store_item: PRepository[StoreItem],
                 ) -> None:
        self.repositories: dict[Type[Any], PRepository[Any]] = {
            CustomerOrder: customer_order,
            StoreItem: store_item,
        }

    def create(self, items: list[ModelType]) -> None:
        for item in items:
            self.repositories[type(item)].create([item])

    def get_by_attribute(self, entity_type: Type[ModelType], attribute_name: str, values: list[Any]) -> list[ModelType]:
        if entity_type in self.repositories:
            return cast(list[ModelType], self.repositories[entity_type].read_by_attribute(attribute_name, values))
        raise NotImplementedError
    
    def update(self, items: list[ModelType]) -> None:
        for item in items:
            self.repositories[type(item)].update([item])
    
    def delete(self, items: list[ModelType]) -> None:
        for item in items:
            self.repositories[type(item)].delete([item])


class ResourceContainer:
    def __init__(self):
        self.resources: dict[Type[Any], list[Any]] = {
            CustomerOrder: [],
            StoreItem: []
        }
    
    def _get_resource_by_type(self, resource_type: Type[ModelType]) -> list[ModelType]:
        if resource_type in self.resources:
            return cast(list[ModelType], self.resources[resource_type])
        raise NotImplementedError(f"No resource for {resource_type}")
    
    def fill(self, model_type: Type[ModelType], items: list[ModelType]) -> None:
        self.resources[model_type].extend(items)
    
    def get_by_attribute(self, model_type: Type[ModelType], 
                         attribute_name: str, 
                         values: list[Any]) -> list[ModelType]:
        
        resource: list[ModelType] = self._get_resource_by_type(model_type)
        
        result: list[ModelType] = []
        for item in resource:
            if getattr(item, attribute_name) in values:
                result.append(item)
        return result
    
    def get_by_id(self, model_type: Type[ModelType], entity_id: EntityId) -> ModelType:
        result: list[ModelType] = self.get_by_attribute(model_type, "entity_id", [entity_id])

        if not result:
            raise RuntimeError(f"Could not find {model_type} with id {entity_id}")
        
        if len(result) > 1:
            raise RuntimeError(f"Found more than one {model_type} with id {entity_id}")

        return result[0]


class ResourceManager:
    def __init__(self, repository_container: RepositoryContainer) -> None:
        self.repository_container = repository_container
        self.resources: ResourceContainer = ResourceContainer()

    def _load_single(self, query: LoadQuery[ModelType, ExtractedAttributeType]) -> None:     
        loaded: list[ModelType] = self.repository_container\
            .get_by_attribute(query.model_type, 
                                      query.attribute_provider.attribute_name, 
                                      query.attribute_provider.get())
        self.resources.fill(query.model_type, loaded)
        
        query.result = loaded
        query.is_loaded = True

    def load(self, queries: list[LoadQuery[Any, Any]]) -> ResourceContainer:
        for query in queries:
            self._load_single(query)
        
        return self.resources