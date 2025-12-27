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

from shop_project.application.manager.commands.shipment_manager_service import (
    ShipmentManagerService,
)
from shop_project.application.manager.schemas.shipment_schema import (
    CreateShipmentSchema,
    ShipmentItemSchema,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.domain.entities.manager import Manager
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.shipment import Shipment, ShipmentState
from shop_project.domain.entities.shipment_summary import (
    ShipmentSummary,
    ShipmentSummaryReason,
)
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.subject import Subject
from tests.helpers import AggregateContainer


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_shipment_manager_service_create(
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    async_container: AsyncContainer,
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    manager_container_factory: Callable[[], AggregateContainer],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
) -> None:
    purchase_draft_service = await async_container.get(ShipmentManagerService)
    manager_container = manager_container_factory()
    potatoes = potatoes_product_10()
    sausages = sausages_product_10()
    container1 = AggregateContainer(aggregate=potatoes, dependencies={})
    container2 = AggregateContainer(aggregate=sausages, dependencies={})
    manager_container.merge(container1)
    manager_container.merge(container2)
    await save_container(manager_container)
    manager: Manager = (
        manager_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_payload = await get_subject_access_token_payload(manager)
    create_shipment_schema = CreateShipmentSchema(
        items=[
            ShipmentItemSchema(
                product_id=potatoes.entity_id,
                amount=10,
            ),
            ShipmentItemSchema(
                product_id=sausages.entity_id,
                amount=10,
            ),
        ],
    )

    shipment_schema = await purchase_draft_service.create_shipment(
        access_payload, create_shipment_schema
    )

    shipment: Shipment = await uow_get_one_single_model(
        Shipment, "entity_id", shipment_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert shipment
    assert shipment.entity_id == shipment_schema.entity_id
    assert shipment.state == ShipmentState.ACTIVE


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_shipment_manager_service_cancel(
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    async_container: AsyncContainer,
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    manager_container_factory: Callable[[], AggregateContainer],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
    uow_get_all_single_model: Callable[
        [Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]
    ],
) -> None:
    purchase_draft_service = await async_container.get(ShipmentManagerService)
    manager_container = manager_container_factory()
    potatoes = potatoes_product_10()
    sausages = sausages_product_10()
    container1 = AggregateContainer(aggregate=potatoes, dependencies={})
    container2 = AggregateContainer(aggregate=sausages, dependencies={})
    manager_container.merge(container1)
    manager_container.merge(container2)
    await save_container(manager_container)
    manager: Manager = (
        manager_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_payload = await get_subject_access_token_payload(manager)
    create_shipment_schema = CreateShipmentSchema(
        items=[
            ShipmentItemSchema(
                product_id=potatoes.entity_id,
                amount=10,
            ),
            ShipmentItemSchema(
                product_id=sausages.entity_id,
                amount=10,
            ),
        ],
    )
    shipment_schema = await purchase_draft_service.create_shipment(
        access_payload, create_shipment_schema
    )

    shipment_summary_schema = await purchase_draft_service.cancel_shipment(
        access_payload, shipment_schema.entity_id
    )

    shipments = await uow_get_all_single_model(Shipment)
    shipment_summary: ShipmentSummary = await uow_get_one_single_model(
        ShipmentSummary, "entity_id", shipment_summary_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert not shipments
    assert shipment_summary
    assert shipment_summary.entity_id == shipment_summary_schema.entity_id
    assert shipment_summary.reason == ShipmentSummaryReason.CANCELLED


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_shipment_manager_service_receive(
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    async_container: AsyncContainer,
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    manager_container_factory: Callable[[], AggregateContainer],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
    uow_get_all_single_model: Callable[
        [Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]
    ],
) -> None:
    purchase_draft_service = await async_container.get(ShipmentManagerService)
    manager_container = manager_container_factory()
    manager: Manager = (
        manager_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    potatoes = potatoes_product_10()
    sausages = sausages_product_10()
    container1 = AggregateContainer(aggregate=potatoes, dependencies={})
    container2 = AggregateContainer(aggregate=sausages, dependencies={})
    manager_container.merge(container1)
    manager_container.merge(container2)
    await save_container(manager_container)
    access_payload = await get_subject_access_token_payload(manager)
    create_shipment_schema = CreateShipmentSchema(
        items=[
            ShipmentItemSchema(
                product_id=potatoes.entity_id,
                amount=10,
            ),
            ShipmentItemSchema(
                product_id=sausages.entity_id,
                amount=10,
            ),
        ],
    )
    shipment_schema = await purchase_draft_service.create_shipment(
        access_payload, create_shipment_schema
    )

    shipment_summary_schema = await purchase_draft_service.receive_shipment(
        access_payload, shipment_schema.entity_id
    )

    shipments = await uow_get_all_single_model(Shipment)
    shipment_summary: ShipmentSummary = await uow_get_one_single_model(
        ShipmentSummary, "entity_id", shipment_summary_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    products_new: list[Product] = await uow_get_all_single_model(
        Product
    )  # pyright: ignore[reportAssignmentType]
    assert not shipments
    assert shipment_summary
    assert shipment_summary.entity_id == shipment_summary_schema.entity_id
    assert shipment_summary.reason == ShipmentSummaryReason.RECEIVED
    for old_item in [potatoes, sausages]:
        for new_item in products_new:
            if old_item.entity_id == new_item.entity_id:
                assert new_item.amount == old_item.amount + 10
