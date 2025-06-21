from typing import Any, Type, TypeVar, cast

from application.interfaces.p_repository import PRepository

from domain.customer_order import CustomerOrder
from domain.store_item import StoreItem


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