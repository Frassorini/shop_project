from decimal import Decimal
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Sequence,
    Type,
)

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.manager.commands.product_manager_service import (
    ProductManagerService,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.schemas.product_schema import (
    ChangeProductSchema,
    CreateProductSchema,
)
from shop_project.domain.entities.manager import Manager
from shop_project.domain.entities.product import Product
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.subject import Subject
from tests.helpers import AggregateContainer


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_product_manager_create(
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    async_container: AsyncContainer,
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    manager_container_factory: Callable[[], AggregateContainer],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
) -> None:
    product_service = await async_container.get(ProductManagerService)
    manager_container = manager_container_factory()
    await save_container(manager_container)
    manager: Manager = (
        manager_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_payload = await get_subject_access_token_payload(manager)

    create_product_schema = CreateProductSchema(
        name="potatoes",
        amount=10,
        price=Decimal(10),
    )

    product_schema = await product_service.create_product(
        access_payload, create_product_schema
    )

    product: Product = await uow_get_one_single_model(
        Product, "entity_id", product_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert product
    assert product_schema.entity_id == product.entity_id
    assert product_schema.name == product.name


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_product_manager_delete(
    async_container: AsyncContainer,
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    manager_container_factory: Callable[[], AggregateContainer],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
    uow_get_all_single_model: Callable[
        [Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]
    ],
) -> None:
    product_service = await async_container.get(ProductManagerService)
    manager_container = manager_container_factory()
    await save_container(manager_container)
    manager: Manager = (
        manager_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_payload = await get_subject_access_token_payload(manager)
    create_product_schema = CreateProductSchema(
        name="potatoes",
        amount=10,
        price=Decimal(10),
    )
    product_schema = await product_service.create_product(
        access_payload, create_product_schema
    )

    await product_service.delete_products(access_payload, [product_schema.entity_id])

    product = await uow_get_all_single_model(Product)
    assert not product


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_product_manager_change(
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    async_container: AsyncContainer,
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    manager_container_factory: Callable[[], AggregateContainer],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
) -> None:
    product_service = await async_container.get(ProductManagerService)
    manager_container = manager_container_factory()
    await save_container(manager_container)
    manager: Manager = (
        manager_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_payload = await get_subject_access_token_payload(manager)
    create_product_schema = CreateProductSchema(
        name="potatoes",
        amount=10,
        price=Decimal(10),
    )
    product_schema = await product_service.create_product(
        access_payload, create_product_schema
    )
    change_product_schema = ChangeProductSchema(
        entity_id=product_schema.entity_id,
        name="potatoes",
        price=Decimal(20),
    )

    product_schema = await product_service.change_product(
        access_payload, change_product_schema
    )

    product: Product = await uow_get_one_single_model(
        Product, "entity_id", product_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert product
    assert product_schema.price == product.price
    assert product_schema.price != create_product_schema.price
