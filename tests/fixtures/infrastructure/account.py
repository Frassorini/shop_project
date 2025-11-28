from typing import Callable

import pytest

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.infrastructure.authentication.helpers.account_factory import (
    create_account,
)
from shop_project.infrastructure.authentication.helpers.subject_type_union import (
    SubjectTypeUnion,
)
from shop_project.infrastructure.entities.account import Account


@pytest.fixture
def subject_account() -> Callable[[SubjectTypeUnion], Account]:
    def _inner(subject: SubjectTypeUnion) -> Account:
        return create_account(subject)

    return _inner


@pytest.fixture
def customer_account(
    subject_account: Callable[[SubjectTypeUnion], Account],
    customer_andrew: Callable[[], Customer],
) -> Callable[[], Account]:
    def _inner() -> Account:
        return subject_account(customer_andrew())

    return _inner


@pytest.fixture
def employee_account(
    subject_account: Callable[[SubjectTypeUnion], Account],
    employee_bob: Callable[[], Employee],
) -> Callable[[], Account]:
    def _inner() -> Account:
        return subject_account(employee_bob())

    return _inner


@pytest.fixture
def manager_account(
    subject_account: Callable[[SubjectTypeUnion], Account],
    manager_tom: Callable[[], Manager],
) -> Callable[[], Account]:
    def _inner() -> Account:
        return subject_account(manager_tom())

    return _inner
