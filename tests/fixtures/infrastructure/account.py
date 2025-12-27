from typing import Callable
from uuid import uuid4

import pytest
from dishka.container import Container

from shop_project.application.entities.account import Account
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.subject import (
    Subject,
)
from shop_project.infrastructure.authentication.services.account_service import (
    AccountService,
)
from tests.helpers import AggregateContainer


@pytest.fixture
def subject_account(
    domain_container: Callable[[], Container],
) -> Callable[[Subject], Account]:
    def _inner(
        subject: Subject,
        phone_number: str | None = None,
        email: str | None = None,
        login: str | None = None,
        password: str | None = None,
    ) -> Account:
        account_service: AccountService = domain_container.get(AccountService)

        if not (login and email and phone_number):
            login = f"login-{uuid4()}"

        if not password:
            password = "password"

        account = account_service.create_account(
            subject=subject,
            login=login,
            phone_number=phone_number,
            email=email,
        )

        account_service.set_password(account=account, password=password)

        return account

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
