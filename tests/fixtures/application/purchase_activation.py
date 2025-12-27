from typing import (
    Awaitable,
    Callable,
    Coroutine,
)
from uuid import uuid4

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.customer.commands.purchase_active_customer_service import (
    PurchaseActiveCustomerService,
)
from shop_project.application.customer.schemas.purchase_active_schema import (
    PurchaseActivationSchema,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.interfaces.subject import Subject
from tests.helpers import AggregateContainer


@pytest.fixture
def purchase_activation(
    async_container: AsyncContainer,
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
) -> Callable[[AggregateContainer], Awaitable[PurchaseActivationSchema]]:
    async def _inner(
        customer_container: AggregateContainer,
    ) -> PurchaseActivationSchema:
        customer: Customer = (
            customer_container.aggregate
        )  # pyright: ignore[reportAssignmentType]

        purchase_draft = PurchaseDraft(uuid4(), customer.entity_id)

        potatoes = potatoes_product_10()
        sausages = sausages_product_10()
        purchase_draft.add_item(potatoes.entity_id, 6)
        purchase_draft.add_item(sausages.entity_id, 6)
        customer_container.dependencies.dependencies[Product] = [potatoes, sausages]
        customer_container.dependencies.dependencies[PurchaseDraft] = [purchase_draft]

        await save_container(customer_container)

        service = await async_container.get(PurchaseActiveCustomerService)

        access_payload = await get_subject_access_token_payload(customer)

        result: PurchaseActivationSchema = await service.activate_draft(
            access_payload, purchase_draft.entity_id
        )
        return result

    return _inner
