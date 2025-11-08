from decimal import Decimal
from typing import Any, Awaitable, Callable, Coroutine, Literal, Type, TypeVar
from dishka.async_container import AsyncContainer
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.domain.base_aggregate import BaseAggregate

from shop_project.domain.services.purchase_claim_service import PurchaseClaimService

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.query.query_builder import QueryPlanBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWork, UnitOfWorkFactory
from shop_project.infrastructure.repositories.repository_container import RepositoryContainer, repository_container_factory
from shop_project.infrastructure.resource_manager.resource_manager import ResourceManager

from shop_project.infrastructure.registries.repository_registry import RepositoryRegistry
from shop_project.infrastructure.registries.resources_registry import ResourcesRegistry
from shop_project.infrastructure.registries.total_order_registry import TotalOrderRegistry

from shop_project.infrastructure.exceptions import UnitOfWorkException, ResourcesException

from tests.helpers import AggregateContainer


@pytest_asyncio.fixture
async def uow_factory(async_container: AsyncContainer)-> UnitOfWorkFactory:
    return await async_container.get(UnitOfWorkFactory)


@pytest.fixture
def uow_delete_and_check(uow_check: Callable[[Type[BaseAggregate], BaseAggregate], UnitOfWork], uow_factory: UnitOfWorkFactory) -> Callable[[Type[BaseAggregate], BaseAggregate], Awaitable[None]]:
    async def _inner(
        model_type: Type[BaseAggregate], 
        domain_object: BaseAggregate) -> None:
        uow = uow_factory.create('read_write')
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

        async with uow_check(model_type, domain_object) as uow2:
            resources = uow2.get_resorces()
            with pytest.raises(ResourcesException):
                resources.get_by_id(model_type, domain_object.entity_id)
        
    return _inner


@pytest.fixture
def uow_check(uow_factory: UnitOfWorkFactory) -> Callable[[Type[BaseAggregate], BaseAggregate], UnitOfWork]:
    def _inner(
        model_type: Type[BaseAggregate], 
        domain_object: BaseAggregate) -> UnitOfWork:
        uow = uow_factory.create('read_only')
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
                            fill_database: Callable[[dict[Type[BaseAggregate], list[BaseAggregate]]], Awaitable[None]]
                            ) -> Callable[[Type[BaseAggregate]], Coroutine[None, None, AggregateContainer]]:
    async def _inner(model_type: Type[BaseAggregate]) -> AggregateContainer:
        domain_container = domain_object_factory(model_type)
        to_fill = domain_container.dependencies.dependencies.copy()

        to_fill.setdefault(model_type, []).append(domain_container.aggregate)
        await fill_database(to_fill)

        return domain_container
    return _inner


@pytest_asyncio.fixture
async def fill_database(uow_factory: UnitOfWorkFactory) -> Callable[[dict[Type[BaseAggregate], list[BaseAggregate]]], Awaitable[None]]:
    async def _fill_db(data: dict[Type[BaseAggregate], list[BaseAggregate]]) -> None:
        uow = uow_factory.create('read_write')
        async with uow:
            for model_type, domain_objects in data.items():
                uow.get_resorces().put_many(model_type, domain_objects)
            await uow.commit()
    return _fill_db
