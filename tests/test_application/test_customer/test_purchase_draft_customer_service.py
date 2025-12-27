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

from shop_project.application.customer.commands.purchase_draft_customer_service import (
    PurchaseDraftCustomerService,
)
from shop_project.application.customer.schemas.purchase_draft_schema import (
    NewPurchaseDraftItemSchema,
    SetNewPurchaseDraftItemsSchema,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_draft import (
    PurchaseDraft,
    PurchaseDraftState,
)
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.subject import Subject
from tests.helpers import AggregateContainer


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_draft_customer_create(
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    async_container: AsyncContainer,
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    customer_container_factory: Callable[[], AggregateContainer],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
) -> None:
    purchase_draft_service = await async_container.get(PurchaseDraftCustomerService)
    customer_container = customer_container_factory()
    await save_container(customer_container)
    customer: Customer = (
        customer_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_payload = await get_subject_access_token_payload(customer)

    purchase_schema = await purchase_draft_service.create_draft(access_payload)

    purchase: PurchaseDraft = await uow_get_one_single_model(
        PurchaseDraft, "entity_id", purchase_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert purchase.customer_id == customer.entity_id
    assert purchase_schema.customer_id == customer.entity_id
    assert purchase.entity_id == purchase_schema.entity_id
    assert purchase.state == PurchaseDraftState.ACTIVE
    assert not purchase.items
    assert not purchase_schema.items


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_draft_customer_change(
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    async_container: AsyncContainer,
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    customer_container_factory: Callable[[], AggregateContainer],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
) -> None:
    purchase_draft_service = await async_container.get(PurchaseDraftCustomerService)
    potatoes = potatoes_product_10()
    sausages = sausages_product_10()
    customer_container = customer_container_factory()
    container1 = AggregateContainer(aggregate=potatoes, dependencies={})
    container2 = AggregateContainer(aggregate=sausages, dependencies={})
    customer_container.merge(container1)
    customer_container.merge(container2)
    await save_container(customer_container)
    customer: Customer = (
        customer_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_payload = await get_subject_access_token_payload(customer)
    purchase_schema = await purchase_draft_service.create_draft(access_payload)

    purchase_schema = await purchase_draft_service.change_products(
        access_payload=access_payload,
        draft_id=purchase_schema.entity_id,
        change=SetNewPurchaseDraftItemsSchema(
            items=[
                NewPurchaseDraftItemSchema(
                    product_id=potatoes.entity_id,
                    amount=10,
                ),
                NewPurchaseDraftItemSchema(
                    product_id=sausages.entity_id,
                    amount=10,
                ),
            ]
        ),
    )

    purchase: PurchaseDraft = await uow_get_one_single_model(
        PurchaseDraft, "entity_id", purchase_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert purchase.customer_id == customer.entity_id
    assert purchase_schema.customer_id == customer.entity_id
    assert purchase.entity_id == purchase_schema.entity_id
    assert purchase.state == PurchaseDraftState.ACTIVE
    assert len(purchase.items) == 2
    assert len(purchase_schema.items) == 2


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_draft_customer_delete(
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    async_container: AsyncContainer,
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
    purchase_draft_container_factory: Callable[[], AggregateContainer],
    uow_get_all_single_model: Callable[
        [Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]
    ],
) -> None:
    purchase_draft_service = await async_container.get(PurchaseDraftCustomerService)
    potatoes = potatoes_product_10()
    sausages = sausages_product_10()
    purchase_draft_container = purchase_draft_container_factory()
    purchase_draft_aggr: PurchaseDraft = (
        purchase_draft_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    purchase_draft_aggr.add_item(potatoes.entity_id, 5)
    purchase_draft_aggr.add_item(sausages.entity_id, 5)
    container1 = AggregateContainer(aggregate=potatoes, dependencies={})
    container2 = AggregateContainer(aggregate=sausages, dependencies={})
    purchase_draft_container.merge(container1)
    purchase_draft_container.merge(container2)
    await save_container(purchase_draft_container)
    customer: Customer = purchase_draft_container.dependencies[Customer][0]
    access_payload = await get_subject_access_token_payload(customer)

    await purchase_draft_service.delete_draft(
        access_payload, purchase_draft_aggr.entity_id
    )

    assert not await uow_get_all_single_model(PurchaseDraft)
