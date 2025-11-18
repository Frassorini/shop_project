from typing import Any, Protocol, Sequence, Type, TypeVar

from shop_project.shared.entity_id import EntityId

from shop_project.domain.base_aggregate import BaseAggregate


T = TypeVar('T', bound=BaseAggregate)


class IResourceContainer(Protocol):
    def __init__(self, resources_registry: list[Type[BaseAggregate]]) -> None:
        ...
    
    def _get_resource_by_type(self, resource_type: Type[T]) -> list[T]:
        ...
    
    def get_by_attribute(self, model_type: Type[T], 
                         attribute_name: str, 
                         values: list[Any]) -> list[T]:
        ...
    
    def get_by_id(self, model_type: Type[T], entity_id: EntityId) -> T:
        ...
    
    def get_by_ids(self, model_type: Type[T], entity_ids: list[EntityId]) -> list[T]:
        ...
    
    def get_all(self, model_type: Type[T]) -> Sequence[T]:
        ...
    
    def put(self, model_type: Type[BaseAggregate], item: BaseAggregate) -> None:
        ...
        
    def put_many(self, model_type: Type[BaseAggregate], items: list[BaseAggregate]) -> None:
        ...
    
    def delete(self, model_type: Type[BaseAggregate], item: BaseAggregate) -> None:
        ...
    
    def delete_many(self, model_type: Type[BaseAggregate], items: Sequence[BaseAggregate]) -> None:
        ...