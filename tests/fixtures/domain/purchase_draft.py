from typing import Callable
from uuid import UUID

import pytest

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from tests.helpers import AggregateContainer


@pytest.fixture
def purchase_draft_factory(
    unique_id_factory: Callable[[], UUID], customer_andrew: Callable[[], Customer]
) -> Callable[[], PurchaseDraft]:
    def factory() -> PurchaseDraft:
        cart = PurchaseDraft(
            unique_id_factory(), customer_id=customer_andrew().entity_id
        )
        return cart

    return factory


@pytest.fixture
def purchase_draft_container_factory(
    unique_id_factory: Callable[[], UUID],
    customer_container_factory: Callable[..., AggregateContainer],
) -> Callable[[], AggregateContainer]:
    def factory() -> AggregateContainer:
        customer_container = customer_container_factory()
        customer = customer_container.aggregate
        cart = PurchaseDraft(unique_id_factory(), customer_id=customer.entity_id)

        container = AggregateContainer(
            aggregate=cart, dependencies={Customer: [customer]}
        )

        container.merge(customer_container)

        return container

    return factory
