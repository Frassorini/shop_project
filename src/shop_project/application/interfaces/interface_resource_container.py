from typing import Any, Protocol, Sequence, Type, TypeVar

from shop_project.shared.entity_id import EntityId

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


T = TypeVar('T', bound=PersistableEntity)


class IResourceContainer(Protocol):
    def __init__(self, resources_registry: list[Type[PersistableEntity]]) -> None:
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
    
    def put(self, model_type: Type[PersistableEntity], item: PersistableEntity) -> None:
        ...
        
    def put_many(self, model_type: Type[PersistableEntity], items: list[PersistableEntity]) -> None:
        ...
    
    def delete(self, model_type: Type[PersistableEntity], item: PersistableEntity) -> None:
        ...
    
    def delete_many(self, model_type: Type[PersistableEntity], items: Sequence[PersistableEntity]) -> None:
        ...