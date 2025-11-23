from typing import Callable
from uuid import UUID

import pytest

from shop_project.domain.entities.customer import Customer


@pytest.fixture
def customer_andrew(
    unique_id_factory: Callable[[], UUID],
) -> Callable[[], Customer]:
    return lambda: Customer(unique_id_factory(), name="andrew")


@pytest.fixture
def customer_bob(unique_id_factory: Callable[[], UUID]) -> Callable[[], Customer]:
    return lambda: Customer(unique_id_factory(), name="bob")
