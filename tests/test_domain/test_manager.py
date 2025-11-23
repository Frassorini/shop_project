from uuid import uuid4

from shop_project.domain.entities.manager import Manager


def test_create_employee() -> None:
    entity_id = uuid4()
    customer = Manager(entity_id, name="Andrew")
    assert customer.name == "Andrew"
