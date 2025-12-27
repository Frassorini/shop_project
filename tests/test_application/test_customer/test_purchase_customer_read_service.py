from typing import (
    Awaitable,
    Callable,
    Coroutine,
    Type,
)

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.customer.queries.purchase_customer_read_service import (
    PurchaseCustomerReadService,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_draft import (
    PurchaseDraft,
)
from shop_project.domain.entities.purchase_summary import (
    PurchaseSummary,
)
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.subject import Subject
from tests.helpers import AggregateContainer


@pytest.mark.asyncio
async def test_purchase_draft_customer_service(
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
    async_container: AsyncContainer,
) -> None:

    model_type: Type[PersistableEntity] = PurchaseDraft
    domain_container: AggregateContainer = await prepare_container(model_type)
    purchase_customer_read_service = await async_container.get(
        PurchaseCustomerReadService
    )
    customer = domain_container.dependencies[Customer][0]
    purchase_draft: PurchaseDraft = (
        domain_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_token = await get_subject_access_token_payload(customer)

    purchase_draft_schemas = await purchase_customer_read_service.get_drafts_by_ids(
        access_payload=access_token, ids=[purchase_draft.entity_id]
    )

    assert len(purchase_draft_schemas) == 1
    assert purchase_draft_schemas[0].entity_id == purchase_draft.entity_id


@pytest.mark.asyncio
async def test_purchase_active_customer_service(
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
    async_container: AsyncContainer,
) -> None:

    model_type: Type[PersistableEntity] = PurchaseActive
    domain_container: AggregateContainer = await prepare_container(model_type)
    purchase_customer_read_service = await async_container.get(
        PurchaseCustomerReadService
    )
    customer = domain_container.dependencies[Customer][0]
    purchase: PurchaseActive = (
        domain_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_token = await get_subject_access_token_payload(customer)

    purchase_draft_schemas = await purchase_customer_read_service.get_actives_by_ids(
        access_payload=access_token, ids=[purchase.entity_id]
    )

    assert len(purchase_draft_schemas) == 1
    assert purchase_draft_schemas[0].entity_id == purchase.entity_id


@pytest.mark.asyncio
async def test_purchase_summary_customer_service(
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
    async_container: AsyncContainer,
) -> None:

    model_type: Type[PersistableEntity] = PurchaseSummary
    domain_container: AggregateContainer = await prepare_container(model_type)
    purchase_customer_read_service = await async_container.get(
        PurchaseCustomerReadService
    )
    customer = domain_container.dependencies[Customer][0]
    purchase: PurchaseSummary = (
        domain_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_token = await get_subject_access_token_payload(customer)

    purchase_draft_schemas = await purchase_customer_read_service.get_summaries_by_ids(
        access_payload=access_token, ids=[purchase.entity_id]
    )

    assert len(purchase_draft_schemas) == 1
    assert purchase_draft_schemas[0].entity_id == purchase.entity_id
