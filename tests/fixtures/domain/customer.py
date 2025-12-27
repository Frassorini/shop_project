from typing import Callable
from uuid import UUID

import pytest

from shop_project.application.entities.account import Account
from shop_project.domain.entities.customer import Customer
from shop_project.domain.interfaces.subject import (
    Subject,
)
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
    subject_account: Callable[[Subject], Account],
) -> Callable[..., AggregateContainer]:

    def fact() -> AggregateContainer:

        customer = customer_andrew()
        account = subject_account(customer)

        return AggregateContainer(aggregate=customer, dependencies={Account: [account]})

    return fact
