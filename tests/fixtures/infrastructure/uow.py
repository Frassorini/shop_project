from decimal import Decimal
from typing import Any, Awaitable, Callable, Coroutine, Literal, Type, TypeVar
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.domain.base_aggregate import BaseAggregate

from shop_project.domain.services.purchase_claim_service import PurchaseClaimService

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.query.query_builder import QueryPlanBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWork
from shop_project.infrastructure.repositories.repository_container import RepositoryContainer, repository_container_factory

from shop_project.exceptions import UnitOfWorkException, ResourcesException

from tests.helpers import AggregateContainer


@pytest.fixture
def uow_factory():
    def factory(session: AsyncSession, mode: Literal["read_only", "read_write"]) -> UnitOfWork:
        repository_container: RepositoryContainer = repository_container_factory(session)
 
        return UnitOfWork(session, repository_container, mode=mode)
    
    return factory


@pytest.fixture
def uow_delete_and_check(uow_check: Callable[..., Any]) -> Callable[..., Awaitable[None]]:
    async def _inner(uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
               test_db: Database, 
               model_type: Type[BaseAggregate], 
               domain_object: BaseAggregate) -> None:
        uow = uow_factory(test_db.get_session(), 'read_write')
        uow.set_query_plan(
            QueryPlanBuilder(mutating=False)
            .load(model_type)
            .from_id([domain_object.entity_id.value])
            .no_lock()
        )
        
        uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(model_type).from_id([domain_object.entity_id.value]).for_update()
        )
    
        async with uow:
            resources = uow.get_resorces()
            purchase_summary_from_db: BaseAggregate = resources.get_by_id(model_type, domain_object.entity_id)
            resources.delete(model_type, purchase_summary_from_db)
            await uow.commit()

        async with uow_check(uow_factory, test_db, model_type, domain_object) as uow2:
            resources = uow2.get_resorces()
            with pytest.raises(ResourcesException):
                resources.get_by_id(model_type, domain_object.entity_id)
        
    return _inner


@pytest.fixture
def uow_check() -> Callable[..., UnitOfWork]:
    def _inner(uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
               test_db: Database, 
               model_type: Type[BaseAggregate], 
               domain_object: BaseAggregate) -> UnitOfWork:
        uow = uow_factory(test_db.get_session(), 'read_only')
        uow.set_query_plan(
            QueryPlanBuilder(mutating=False)
            .load(model_type)
            .from_id([domain_object.entity_id.value])
            .no_lock()
        )
        return uow
    return _inner


@pytest.fixture
def prepare_container(domain_object_factory: Callable[[Type[BaseAggregate]], AggregateContainer], 
                            fill_database: Callable[[Database, dict[Type[BaseAggregate], list[BaseAggregate]]], Coroutine[None, None, Database]]
                            ) -> Callable[[Type[BaseAggregate], Database], Coroutine[None, None, AggregateContainer]]:
    async def _prepare(model_type: Type[BaseAggregate], test_db: Database) -> AggregateContainer:
        domain_container = domain_object_factory(model_type)
        to_fill = domain_container.dependencies.dependencies.copy()

        to_fill.setdefault(model_type, []).append(domain_container.aggregate)
        await fill_database(test_db, to_fill)

        return domain_container
    return _prepare