from typing import Callable
from uuid import UUID

import pytest

from shop_project.domain.entities.customer import Customer
from shop_project.infrastructure.entities.account import Account, SubjectType
from tests.helpers import AggregateContainer


@pytest.fixture
def customer_andrew(
    unique_id_factory: Callable[[], UUID],
) -> Callable[[], Customer]:
    return lambda: Customer(unique_id_factory(), name="andrew")


@pytest.fixture
def customer_bob(unique_id_factory: Callable[[], UUID]) -> Callable[[], Customer]:
    return lambda: Customer(unique_id_factory(), name="bob")


@pytest.fixture
def customer_container_factory(
    customer_andrew: Callable[[], Customer],
) -> Callable[..., AggregateContainer]:

    def fact() -> AggregateContainer:

        customer = customer_andrew()
        account = Account(customer.entity_id, subject_type=SubjectType.CUSTOMER)

        return AggregateContainer(aggregate=customer, dependencies={Account: [account]})

    return fact
