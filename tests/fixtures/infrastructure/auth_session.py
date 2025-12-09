from typing import Callable
from uuid import UUID

import pytest
from dishka.container import Container

from shop_project.domain.entities.customer import Customer
from shop_project.domain.interfaces.subject import (
    Subject,
)
from shop_project.infrastructure.authentication.services.session_service import (
    SessionService,
)
from shop_project.infrastructure.entities.account import Account
from tests.helpers import AggregateContainer


@pytest.fixture
def get_account_id_by_access_token(
    domain_container: Callable[[], Container],
) -> Callable[[str], UUID]:
    def _inner(access_token: str) -> UUID:
        account_service: SessionService = domain_container.get(SessionService)
        payload = account_service.verify_access_token(access_token)
        if not payload:
            raise ValueError
        return payload.account_id

    return _inner


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
