from typing import AsyncContextManager, Protocol, Type
from uuid import UUID

from shop_project.application.interfaces.interface_query_plan import IQueryPlan
from shop_project.application.interfaces.interface_resource_container import (
    IResourceContainer,
)
from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class ConcurrencyException(Exception):
    """Base class for all concurrency-related errors."""


class NoWaitException(ConcurrencyException):
    """Resource is busy while nowait is set."""


class LockTimeoutException(ConcurrencyException):
    """Lock wait timeout."""


class DeadlockDetectedException(ConcurrencyException):
    """Deadlock detected, operation should be retried."""


class IUnitOfWork(Protocol):
    def get_resorces(self) -> IResourceContainer: ...

    def get_unique_id(self, model_type: type[PersistableEntity]) -> UUID: ...

    def mark_commit(self) -> None: ...

    @property
    def commit_requested(self) -> bool: ...


class IUnitOfWorkFactory(Protocol):
    def create(
        self,
        query_plan: IQueryPlan,
        exception_on_nowait: Type[Exception] | None = None,
        wait_timeout_ms: int | None = None,
    ) -> AsyncContextManager[IUnitOfWork]: ...
