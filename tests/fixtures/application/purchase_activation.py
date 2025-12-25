from typing import (
    Awaitable,
    Callable,
    Coroutine,
    Type,
    cast,
)

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.customer.commands.purchase_flow_service import (
    PurchaseFlowService,
)
from shop_project.application.customer.schemas.purchase_active_schema import (
    PurchaseActivationSchema,
)
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from tests.helpers import AggregateContainer


@pytest.fixture
def purchase_activation(
    async_container: AsyncContainer,
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    domain_object_factory: Callable[[Type[PersistableEntity]], AggregateContainer],
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
) -> Callable[[], Awaitable[PurchaseActivationSchema]]:
    async def _inner() -> PurchaseActivationSchema:
        aggregate_container: AggregateContainer = domain_object_factory(PurchaseDraft)
        aggregate: PurchaseDraft = cast(PurchaseDraft, aggregate_container.aggregate)
        customer: Customer = aggregate_container.dependencies[Customer][0]

        potatoes = potatoes_product_10()
        sausages = sausages_product_10()
        assert len(aggregate.items) == 0
        aggregate.add_item(potatoes.entity_id, 6)
        aggregate.add_item(sausages.entity_id, 6)
        aggregate_container.dependencies.dependencies[Product] = [potatoes, sausages]

        await save_container(aggregate_container)

        service = await async_container.get(PurchaseFlowService)

        result: PurchaseActivationSchema = await service.activate_draft(
            customer.entity_id, aggregate.entity_id
        )
        return result

    return _inner
