from typing import Callable
from uuid import UUID

import pytest

from shop_project.application.entities.account import Account
from shop_project.domain.entities.employee import Employee
from shop_project.domain.interfaces.subject import (
    Subject,
)
from tests.helpers import AggregateContainer


@pytest.fixture
def employee_bob(
    unique_id_factory: Callable[[], UUID],
) -> Callable[[], Employee]:
    return lambda: Employee(unique_id_factory(), name="bob")


@pytest.fixture
def employee_container_factory(
    employee_bob: Callable[[], Employee],
    subject_account: Callable[[Subject], Account],
) -> Callable[..., AggregateContainer]:

    def fact() -> AggregateContainer:

        customer = employee_bob()
        account = subject_account(customer)

        return AggregateContainer(aggregate=customer, dependencies={Account: [account]})

    return fact
