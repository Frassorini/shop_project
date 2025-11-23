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
    unique_id_factory: Callable[[], UUID], customer_andrew: Callable[[], Customer]
) -> Callable[[], AggregateContainer]:
    def factory() -> AggregateContainer:
        customer = customer_andrew()
        cart = PurchaseDraft(unique_id_factory(), customer_id=customer.entity_id)

        container = AggregateContainer(
            aggregate=cart, dependencies={Customer: [customer]}
        )
        return container

    return factory
