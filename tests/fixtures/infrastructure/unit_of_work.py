from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Any, AsyncContextManager, AsyncGenerator, AsyncIterator, Awaitable, Callable, Coroutine, Literal, Type, TypeVar
from dishka.async_container import AsyncContainer
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.domain.persistable_entity import PersistableEntity

from shop_project.domain.services.purchase_claim_service import PurchaseClaimService

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.query.query_builder import QueryBuilder
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
def uow_delete_and_check(uow_check: Callable[[Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]], uow_factory: UnitOfWorkFactory) -> Callable[[Type[PersistableEntity], PersistableEntity], Awaitable[None]]:
    async def _inner(model_type: Type[PersistableEntity], 
                     domain_object: PersistableEntity) -> None:
        async with uow_factory.create(
            QueryBuilder(mutating=True)
            .load(model_type).from_id([domain_object.entity_id.value]).for_update()
        ) as uow:
            resources = uow.get_resorces()
            purchase_summary_from_db: PersistableEntity = resources.get_by_id(model_type, domain_object.entity_id)
            resources.delete(model_type, purchase_summary_from_db)
            uow.mark_commit()

        async with uow_check(model_type, domain_object) as uow2:
            resources = uow2.get_resorces()
            with pytest.raises(ResourcesException):
                resources.get_by_id(model_type, domain_object.entity_id)
        
    return _inner


@pytest.fixture
def uow_check(uow_factory: UnitOfWorkFactory) -> Callable[[Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]]:
    @asynccontextmanager
    async def _inner(
        model_type: Type[PersistableEntity], 
        domain_object: PersistableEntity) -> AsyncIterator[UnitOfWork]:
        async with uow_factory.create(
            QueryBuilder(mutating=False)
            .load(model_type)
            .from_id([domain_object.entity_id.value])
            .no_lock()
        ) as uow:
            yield uow
    return _inner


@pytest.fixture
def prepare_container(domain_object_factory: Callable[[Type[PersistableEntity]], AggregateContainer], 
                            fill_database: Callable[[dict[Type[PersistableEntity], list[PersistableEntity]]], Awaitable[None]]
                            ) -> Callable[[Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]]:
    async def _inner(model_type: Type[PersistableEntity]) -> AggregateContainer:
        domain_container = domain_object_factory(model_type)
        to_fill = domain_container.dependencies.dependencies.copy()

        to_fill.setdefault(model_type, []).append(domain_container.aggregate)
        await fill_database(to_fill)

        return domain_container
    return _inner


@pytest_asyncio.fixture
async def fill_database(uow_factory: UnitOfWorkFactory) -> Callable[[dict[Type[PersistableEntity], list[PersistableEntity]]], Awaitable[None]]:
    async def _fill_db(data: dict[Type[PersistableEntity], list[PersistableEntity]]) -> None:
        async with uow_factory.create(QueryBuilder(mutating=True)) as uow:
            for model_type, domain_objects in data.items():
                uow.get_resorces().put_many(model_type, domain_objects)
            uow.mark_commit()
    return _fill_db
