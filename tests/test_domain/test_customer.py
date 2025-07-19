from shop_project.domain.customer import Customer
from shop_project.shared.entity_id import EntityId


def test_create_customer() -> None:
    customer = Customer(EntityId('1'), name='Andrew')
    assert customer.name == 'Andrew'


def test_snapshot_customer() -> None:
    customer = Customer(EntityId('1'), name='Andrew')
    assert customer.snapshot() == {'entity_id': '1', 'name': 'Andrew'}


def test_from_snapshot_customer() -> None:
    customer = Customer.from_snapshot({'entity_id': '1', 'name': 'Andrew'})
    assert customer.name == 'Andrew'