from uuid import uuid4

from shop_project.domain.entities.employee import Employee


def test_create_employee() -> None:
    entity_id = uuid4()
    customer = Employee(entity_id, name="Andrew")
    assert customer.name == "Andrew"
