from typing import Callable

import pytest
from dishka.container import Container
from pydantic_extra_types.phone_numbers import PhoneNumber

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.subject import (
    Subject,
)
from shop_project.infrastructure.authentication.services.account_service import (
    AccountService,
)
from shop_project.infrastructure.entities.account import Account
from tests.helpers import AggregateContainer


@pytest.fixture
def subject_account(
    domain_container: Callable[[], Container],
) -> Callable[[Subject], Account]:
    def _inner(subject: Subject) -> Account:
        account_service: AccountService = domain_container.get(AccountService)

        return account_service.create_account(
            subject=subject, phone_number=PhoneNumber("+7(999)999-99-99"), email=None
        )

    return _inner


@pytest.fixture
def customer_account(
    subject_account: Callable[[Subject], Account],
    customer_andrew: Callable[[], Customer],
) -> Callable[[], Account]:
    def _inner() -> Account:
        return subject_account(customer_andrew())

    return _inner


@pytest.fixture
def employee_account(
    subject_account: Callable[[Subject], Account],
    employee_bob: Callable[[], Employee],
) -> Callable[[], Account]:
    def _inner() -> Account:
        return subject_account(employee_bob())

    return _inner


@pytest.fixture
def manager_account(
    subject_account: Callable[[Subject], Account],
    manager_tom: Callable[[], Manager],
) -> Callable[[], Account]:
    def _inner() -> Account:
        return subject_account(manager_tom())

    return _inner


@pytest.fixture
def account_container_factory(
    customer_andrew: Callable[[], Customer],
    subject_account: Callable[[Subject], Account],
) -> Callable[..., AggregateContainer]:

    def fact() -> AggregateContainer:

        customer = customer_andrew()
        account = subject_account(customer)

        return AggregateContainer(aggregate=account, dependencies={})

    return fact
