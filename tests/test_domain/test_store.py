from uuid import UUID, uuid4

from shop_project.domain.store import Store
from shop_project.shared.entity_id import EntityId


def test_create_store() -> None:
    entity_id = EntityId(uuid4())
    store = Store(entity_id, name='Moscow')
    assert store.name == 'Moscow'


def test_snapshot_store() -> None:
    entity_id = EntityId(uuid4())
    store = Store(entity_id, name='Moscow')
    assert store.to_dict() == {'entity_id': entity_id.value, 'name': 'Moscow'}


def test_from_snapshot_store() -> None:
    entity_id = EntityId(uuid4())
    store = Store.from_dict({'entity_id': entity_id.value, 'name': 'Moscow'})
    assert store.name == 'Moscow'