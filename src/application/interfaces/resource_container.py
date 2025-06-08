from typing import Any, Type, TypeVar, cast
from application.repositories.p_repository import PRepository
from application.repositories.store_item_repository import StoreItemRepository
from domain.customer import Customer
from domain.customer_order.model import CustomerOrder
from domain.store_item.model import StoreItem
from application.interfaces.load_query import LoadQuery
from application.repositories.customer_order_repository import CustomerOrderRepository
from shared.entity_id import EntityId


T = TypeVar('T', CustomerOrder, StoreItem)


class RepositoryContainer:
    def __init__(self) -> None:
        self.repositories: dict[Type[Any], PRepository[Any]] = {
            CustomerOrder: CustomerOrderRepository({}),
            StoreItem: StoreItemRepository({}),
        }

    def get_entities_by_criteria(self, entity_type: Type[T], criteria: str, values: list[Any]) -> list[T]:
        if entity_type in self.repositories:
            return cast(list[T], self.repositories[entity_type].get_by_criteria(criteria, values))
        raise NotImplementedError


class ResourceContainer:
    def __init__(self) -> None:
        self.repository_container = RepositoryContainer()
        self.resources: dict[Type[Any], list[Any]] = {
            CustomerOrder: [],
            StoreItem: []
        }

    def _get_resource_by_type(self, resource_type: Type[T]) -> list[T]:
        if resource_type in self.resources:
            return cast(list[T], self.resources[resource_type])
        raise NotImplementedError(f"No resource for {resource_type}")

    def _load_single(self, query: LoadQuery[T]) -> None:
        ids = query.id_provider.extract()
        model_type = query.model_type
        loaded: list[T] = self.repository_container.get_entities_by_criteria(model_type, 'entity_id', ids)
        
        resource: list[T] = self._get_resource_by_type(model_type)
        resource.extend(loaded)
        query.result = loaded

        query.is_loaded = True

    def load(self, queries: list[LoadQuery[Any]]) -> None:
        for query in queries:
            self._load_single(query)
    
    def get_by_id(self, model_type: Type[T], id: EntityId) -> T:
        resource: list[T] = self._get_resource_by_type(model_type)
        for item in resource:
            if item.entity_id == id:
                return item
        raise RuntimeError(f"Item with id {id} not found")