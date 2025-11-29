from typing import Callable

import pytest
from dishka.container import Container
from pydantic import SecretStr

from shop_project.domain.entities.customer import Customer
from shop_project.domain.interfaces.subject import (
    Subject,
)
from shop_project.infrastructure.authentication.helpers.credential import Credential
from shop_project.infrastructure.authentication.services.secret_service import (
    SecretService,
)
from shop_project.infrastructure.authentication.services.session_service import (
    SessionService,
)
from shop_project.infrastructure.entities.account import Account
from shop_project.infrastructure.entities.secret import AuthType
from tests.helpers import AggregateContainer


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


@pytest.fixture
def auth_session_container_factory(
    customer_andrew: Callable[[], Customer],
    subject_account: Callable[[Subject], Account],
    domain_container: Container,
) -> Callable[..., AggregateContainer]:

    def fact() -> AggregateContainer:
        session_service = domain_container.get(SessionService)

        customer = customer_andrew()
        account = subject_account(customer)

        session, sesion_refresh = session_service.create_session(account, customer)

        return AggregateContainer(
            aggregate=session, dependencies={Customer: [customer], Account: [account]}
        )

    return fact


@pytest.fixture
def secret_container_factory(
    customer_andrew: Callable[[], Customer],
    subject_account: Callable[[Subject], Account],
    domain_container: Container,
) -> Callable[..., AggregateContainer]:

    def fact() -> AggregateContainer:
        secret_service = domain_container.get(SecretService)

        customer = customer_andrew()
        account = subject_account(customer)

        secret = secret_service.create_secret(
            account_id=account.entity_id,
            credential=Credential(
                auth_type=AuthType.PASSWORD, payload={"password": SecretStr("password")}
            ),
        )

        return AggregateContainer(
            aggregate=secret, dependencies={Customer: [customer], Account: [account]}
        )

    return fact
