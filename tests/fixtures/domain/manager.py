from typing import Callable
from uuid import UUID

import pytest

from shop_project.domain.entities.manager import Manager
from shop_project.infrastructure.authentication.helpers.subject_type_union import (
    SubjectTypeUnion,
)
from shop_project.infrastructure.entities.account import Account
from tests.helpers import AggregateContainer


@pytest.fixture
def manager_tom(
    unique_id_factory: Callable[[], UUID],
) -> Callable[[], Manager]:
    return lambda: Manager(unique_id_factory(), name="tom")


@pytest.fixture
def manager_container_factory(
    manager_tom: Callable[[], Manager],
    subject_account: Callable[[SubjectTypeUnion], Account],
) -> Callable[..., AggregateContainer]:

    def fact() -> AggregateContainer:

        manager = manager_tom()
        account = subject_account(manager)

        return AggregateContainer(aggregate=manager, dependencies={Account: [account]})

    return fact
