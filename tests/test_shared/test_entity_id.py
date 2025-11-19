from uuid import uuid4

from shop_project.shared.entity_id import EntityId


def test_entity_id():
    uuid_id = uuid4()
    entity_id = EntityId(uuid_id)

    assert entity_id.value == uuid_id


def test_equal():
    uuid_id = uuid4()
    entity_id1 = EntityId(uuid_id)
    entity_id2 = EntityId(uuid_id)

    assert entity_id1 == entity_id2


def test_not_equal():
    uuid_id_1 = uuid4()
    uuid_id_2 = uuid4()
    entity_id1 = EntityId(uuid_id_1)
    entity_id2 = EntityId(uuid_id_2)

    assert entity_id1 != entity_id2
