from contextlib import asynccontextmanager
from typing import (
    AsyncContextManager,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Sequence,
    Type,
)

import pytest
import pytest_asyncio
from dishka.async_container import AsyncContainer

from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.exceptions import ResourcesException
from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWork, UnitOfWorkFactory
from tests.helpers import AggregateContainer


@pytest_asyncio.fixture
async def uow_factory(async_container: AsyncContainer) -> UnitOfWorkFactory:
    return await async_container.get(UnitOfWorkFactory)


@pytest.fixture
def uow_delete_and_check(
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
    uow_factory: UnitOfWorkFactory,
) -> Callable[[Type[PersistableEntity], PersistableEntity], Awaitable[None]]:
    async def _inner(
        model_type: Type[PersistableEntity], domain_object: PersistableEntity
    ) -> None:
        async with uow_factory.create(
            QueryBuilder(mutating=True)
            .load(model_type)
            .from_id([domain_object.entity_id])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resorces()
            purchase_summary_from_db: PersistableEntity = resources.get_by_id(
                model_type, domain_object.entity_id
            )
            resources.delete(model_type, purchase_summary_from_db)
            uow.mark_commit()

        async with uow_check(model_type, domain_object) as uow2:
            resources = uow2.get_resorces()
            with pytest.raises(ResourcesException):
                resources.get_by_id(model_type, domain_object.entity_id)

    return _inner


@pytest.fixture
def uow_check(
    uow_factory: UnitOfWorkFactory,
) -> Callable[
    [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
]:
    @asynccontextmanager
    async def _inner(
        model_type: Type[PersistableEntity], domain_object_id: PersistableEntity
    ) -> AsyncIterator[UnitOfWork]:
        async with uow_factory.create(
            QueryBuilder(mutating=False)
            .load(model_type)
            .from_id([domain_object_id.entity_id])
            .no_lock()
            .build()
        ) as uow:
            yield uow

    return _inner


@pytest.fixture
def uow_get_all_single_model(
    uow_factory: UnitOfWorkFactory,
) -> Callable[[Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]]:
    async def _inner(
        model_type: Type[PersistableEntity],
    ) -> Sequence[PersistableEntity]:
        async with uow_factory.create(
            QueryBuilder(mutating=False).load(model_type).no_lock().build()
        ) as uow:
            resources = uow.get_resorces()
            return resources.get_all(model_type)

    return _inner


@pytest.fixture
def uow_get_one_single_model(
    uow_factory: UnitOfWorkFactory,
) -> Callable[[Type[PersistableEntity], str, str], Awaitable[PersistableEntity]]:
    async def _inner(
        model_type: Type[PersistableEntity], attribute_name: str, attribute_value: str
    ) -> PersistableEntity:
        async with uow_factory.create(
            QueryBuilder(mutating=False)
            .load(model_type)
            .from_attribute(attribute_name, [attribute_value])
            .no_lock()
            .build()
        ) as uow:
            resources = uow.get_resorces()
            return resources.get_one_by_attribute(
                model_type, attribute_name, attribute_value
            )

    return _inner


@pytest.fixture
def uow_get_many_single_model(
    uow_factory: UnitOfWorkFactory,
) -> Callable[
    [Type[PersistableEntity], str, list[str]], Awaitable[Sequence[PersistableEntity]]
]:
    async def _inner(
        model_type: Type[PersistableEntity],
        attribute_name: str,
        attribute_values: list[str],
    ) -> Sequence[PersistableEntity]:
        async with uow_factory.create(
            QueryBuilder(mutating=False)
            .load(model_type)
            .from_attribute(attribute_name, attribute_values)
            .no_lock()
            .build()
        ) as uow:
            resources = uow.get_resorces()
            return resources.get_by_attribute(
                model_type, attribute_name, attribute_values
            )

    return _inner


@pytest.fixture
def prepare_container(
    domain_object_factory: Callable[[Type[PersistableEntity]], AggregateContainer],
    fill_database: Callable[
        [dict[Type[PersistableEntity], list[PersistableEntity]]], Awaitable[None]
    ],
) -> Callable[[Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]]:
    async def _inner(model_type: Type[PersistableEntity]) -> AggregateContainer:
        domain_container = domain_object_factory(model_type)
        to_fill = domain_container.dependencies.dependencies.copy()

        to_fill.setdefault(model_type, []).append(domain_container.aggregate)
        await fill_database(to_fill)

        return domain_container

    return _inner


@pytest_asyncio.fixture
async def fill_database(
    uow_factory: UnitOfWorkFactory,
) -> Callable[
    [dict[Type[PersistableEntity], list[PersistableEntity]]], Awaitable[None]
]:
    async def _fill_db(
        data: dict[Type[PersistableEntity], list[PersistableEntity]],
    ) -> None:
        async with uow_factory.create(QueryBuilder(mutating=True).build()) as uow:
            for model_type, domain_objects in data.items():
                uow.get_resorces().put_many(model_type, domain_objects)
            uow.mark_commit()

    return _fill_db
