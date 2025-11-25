from typing import Callable
from uuid import UUID

import pytest

from shop_project.domain.entities.employee import Employee
from shop_project.infrastructure.entities.account import Account, SubjectType
from tests.helpers import AggregateContainer


@pytest.fixture
def employee_bob(
    unique_id_factory: Callable[[], UUID],
) -> Callable[[], Employee]:
    return lambda: Employee(unique_id_factory(), name="bob")


@pytest.fixture
def employee_container_factory(
    employee_bob: Callable[[], Employee],
) -> Callable[..., AggregateContainer]:

    def fact() -> AggregateContainer:

        customer = employee_bob()
        account = Account(customer.entity_id, subject_type=SubjectType.EMPLOYEE)

        return AggregateContainer(aggregate=customer, dependencies={Account: [account]})

    return fact
