from typing import Callable
import pytest

from shop_project.domain.entities.customer import Customer
from shop_project.shared.entity_id import EntityId


@pytest.fixture
def customer_andrew(unique_id_factory: Callable[[], EntityId]) -> Callable[[], Customer]:
    return lambda: Customer(unique_id_factory(), name='andrew')


@pytest.fixture
def customer_bob(unique_id_factory: Callable[[], EntityId]) -> Callable[[], Customer]:
    return lambda: Customer(unique_id_factory(), name='bob')