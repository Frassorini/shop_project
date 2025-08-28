from shop_project.domain.store import Store
from shop_project.shared.entity_id import EntityId


def test_create_store() -> None:
    store = Store(EntityId('1'), name='Moscow')
    assert store.name == 'Moscow'


def test_snapshot_store() -> None:
    store = Store(EntityId('1'), name='Moscow')
    assert store.to_dict() == {'entity_id': '1', 'name': 'Moscow'}


def test_from_snapshot_store() -> None:
    store = Store.from_dict({'entity_id': '1', 'name': 'Moscow'})
    assert store.name == 'Moscow'