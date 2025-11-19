from contextlib import asynccontextmanager
from typing import AsyncContextManager, AsyncGenerator, Literal, Protocol, Self

from shop_project.domain.persistable_entity import PersistableEntity
from shop_project.shared.entity_id import EntityId

from shop_project.application.interfaces.interface_query_builder import IQueryBuilder
from shop_project.application.interfaces.interface_resource_container import IResourceContainer


class IUnitOfWork(Protocol):
    def get_resorces(self) -> IResourceContainer:
        ...
    
    def get_unique_id(self, model_type: type[PersistableEntity]) -> EntityId:
        ...
    
    def mark_commit(self) -> None:
        ...
    
    @property
    def commit_requested(self) -> bool:
        ...

class IUnitOfWorkFactory(Protocol):
    def create(self, query_plan_builder: IQueryBuilder | None = None) -> AsyncContextManager[IUnitOfWork]:
        ...