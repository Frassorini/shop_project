from typing import Literal, Protocol, Self

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.shared.entity_id import EntityId

from shop_project.application.interfaces.interface_query_builder import IQueryBuilder
from shop_project.application.interfaces.interface_resource_container import IResourceContainer


class IUnitOfWork(Protocol):
    def set_query_plan(self, query_plan: IQueryBuilder) -> None:
        ...
    
    async def __aenter__(self) -> Self:
        ...
    
    def get_resorces(self) -> IResourceContainer:
        ...
    
    def get_unique_id(self, model_type: type[BaseAggregate]) -> EntityId:
        ...
    
    async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Exception | None) -> None:
        ...

    async def commit(self) -> None:
        ...
    
    async def rollback(self) -> None:
        ...


class IUnitOfWorkFactory(Protocol):
    
    def create(self, mode: Literal["read_only", "read_write"]) -> IUnitOfWork:
        ...