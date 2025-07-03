from typing import Any, Literal, Type, TypeVar, cast

from application.interfaces.p_repository import PRepository

from domain.customer_order import CustomerOrder
from domain.p_aggregate import PAggregate
from domain.store_item import StoreItem
from infrastructure.p_session import PSession


T = TypeVar('T', bound=PAggregate)


class RepositoryContainer:
    def __init__(self, session: PSession, repositories: dict[Type[PAggregate], PRepository[PAggregate]]) -> None:
        self.session: PSession = session
        self.repositories: dict[Type[PAggregate], PRepository[PAggregate]] = repositories

    def create(self, entity_type: Type[T], items: list[T]) -> None:
        for item in items:
            self.repositories[entity_type].create([item])

    def get_by_attribute(self, entity_type: Type[T], attribute_name: str, values: list[Any]) -> list[T]:
        if entity_type in self.repositories:
            return cast(list[T], self.repositories[entity_type].read_by_attribute(attribute_name, values))
        raise NotImplementedError
    
    def delete(self, items: list[PAggregate]) -> None:
        for item in items:
            self.repositories[type(item)].delete([item])
    
    def save(self, resource_changes: dict[Type[PAggregate], dict[Literal['CREATED', 'UPDATED', 'DELETED'], list[dict[str, Any]]]]) -> None:
        for entity_type, difference in resource_changes.items():
            self.repositories[entity_type].save(difference)
