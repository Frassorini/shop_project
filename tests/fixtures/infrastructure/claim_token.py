from typing import Callable

import pytest
from dishka.container import Container

from shop_project.application.shared.interfaces.interface_claim_token_service import (
    IClaimTokenService,
)
from shop_project.domain.entities.customer import Customer
from tests.helpers import AggregateContainer


@pytest.fixture
def claim_token_container_factory(
    customer_container_factory: Callable[[], AggregateContainer],
    domain_container: Container,
) -> Callable[..., AggregateContainer]:

    def fact() -> AggregateContainer:
        claim_token_service = domain_container.get(IClaimTokenService)

        customer_container = customer_container_factory()
        customer: Customer = (
            customer_container.aggregate
        )  # pyright: ignore[reportAssignmentType]

        claim_token, raw_token = claim_token_service.create(customer.entity_id)

        return AggregateContainer(aggregate=claim_token, dependencies={}).merge(
            customer_container
        )

    return fact
