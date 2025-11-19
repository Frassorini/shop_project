from typing import AsyncContextManager, Protocol

from shop_project.application.interfaces.interface_query_plan import IQueryPlan
from shop_project.application.interfaces.interface_resource_container import (
    IResourceContainer,
)
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.shared.entity_id import EntityId


class IUnitOfWork(Protocol):
    def get_resorces(self) -> IResourceContainer: ...

    def get_unique_id(self, model_type: type[PersistableEntity]) -> EntityId: ...

    def mark_commit(self) -> None: ...

    @property
    def commit_requested(self) -> bool: ...


class IUnitOfWorkFactory(Protocol):
    def create(self, query_plan: IQueryPlan) -> AsyncContextManager[IUnitOfWork]: ...
