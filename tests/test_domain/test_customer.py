from uuid import uuid4

from shop_project.domain.entities.customer import Customer


def test_create_customer() -> None:
    entity_id = uuid4()
    customer = Customer(entity_id, name="Andrew")
    assert customer.name == "Andrew"


def test_snapshot_customer() -> None:
    entity_id = uuid4()
    customer = Customer(entity_id, name="Andrew")
    assert customer.to_dict() == {"entity_id": entity_id, "name": "Andrew"}


def test_from_snapshot_customer() -> None:
    entity_id = uuid4()
    customer = Customer.from_dict({"entity_id": entity_id, "name": "Andrew"})
    assert customer.name == "Andrew"
