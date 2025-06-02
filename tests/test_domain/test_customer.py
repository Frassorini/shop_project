from typing import Callable
from domain.customer import Customer
from domain.entity_id import EntityId


def test_create_customer() -> None:
    customer = Customer(EntityId(1), name='Andrew')
    assert customer.name == 'Andrew'