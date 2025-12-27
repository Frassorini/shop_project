from typing import Callable
from uuid import UUID

import pytest

from shop_project.application.entities.account import Account
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.subject import (
    Subject,
)
from tests.helpers import AggregateContainer


@pytest.fixture
def manager_tom(
    unique_id_factory: Callable[[], UUID],
) -> Callable[[], Manager]:
    return lambda: Manager(unique_id_factory(), name="tom")


@pytest.fixture
def manager_container_factory(
    manager_tom: Callable[[], Manager],
    subject_account: Callable[[Subject], Account],
) -> Callable[..., AggregateContainer]:

    def fact() -> AggregateContainer:

        manager = manager_tom()
        account = subject_account(manager)

        return AggregateContainer(aggregate=manager, dependencies={Account: [account]})

    return fact
