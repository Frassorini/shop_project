from typing import Any, Literal, Type, TypeVar, cast

from shop_project.application.dto.base_dto import BaseDTO
from shop_project.application.interfaces.p_repository import PRepository

from shop_project.domain.customer_order import CustomerOrder
from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.store_item import StoreItem
from shop_project.p_session import PSession
from shop_project.infrastructure.query.load_query import LoadQuery
from shop_project.shared.entity_id import EntityId


T = TypeVar('T', bound=BaseAggregate)


class RepositoryContainer:
    def __init__(self, session: PSession, repositories: dict[Type[BaseAggregate], PRepository[BaseAggregate]]) -> None:
        self.session: PSession = session
        self.repositories: dict[Type[BaseAggregate], PRepository[BaseAggregate]] = repositories
    
    def load_from_query(self, query: LoadQuery) -> list[BaseAggregate]:
        return self.repositories[query.model_type].load_from_query(query)

    def get_by_attribute(self, entity_type: Type[T], attribute_name: str, values: list[str]) -> list[T]:
        if entity_type in self.repositories:
            return cast(list[T], self.repositories[entity_type].read_by_attribute(attribute_name, values))
        raise NotImplementedError
    
    def save(self, resource_changes_snapshot: dict[Type[BaseAggregate], dict[Literal['CREATED', 'UPDATED', 'DELETED'], list[BaseDTO]]]) -> None:
        for entity_type, difference in resource_changes_snapshot.items():
            self.repositories[entity_type].save(difference)
    
    def get_unique_id(self, model_type: type[BaseAggregate]) -> EntityId:
        return self.repositories[model_type].get_unique_id()
