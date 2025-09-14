from uuid import UUID, uuid4

from shop_project.domain.customer import Customer
from shop_project.shared.entity_id import EntityId


def test_create_customer() -> None:
    entity_id = EntityId(uuid4())
    customer = Customer(entity_id, name='Andrew')
    assert customer.name == 'Andrew'


def test_snapshot_customer() -> None:
    entity_id = EntityId(uuid4())
    customer = Customer(entity_id, name='Andrew')
    assert customer.to_dict() == {'entity_id': entity_id.value, 'name': 'Andrew'}


def test_from_snapshot_customer() -> None:
    entity_id = EntityId(uuid4())
    customer = Customer.from_dict({'entity_id': entity_id.value, 'name': 'Andrew'})
    assert customer.name == 'Andrew'