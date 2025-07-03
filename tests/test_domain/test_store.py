from domain.store import Store
from shared.entity_id import EntityId


def test_create_store() -> None:
    store = Store(EntityId('1'), name='Moscow')
    assert store.name == 'Moscow'


def test_snapshot_store() -> None:
    store = Store(EntityId('1'), name='Moscow')
    assert store.snapshot() == {'entity_id': '1', 'name': 'Moscow'}


def test_from_snapshot_store() -> None:
    store = Store.from_snapshot({'entity_id': '1', 'name': 'Moscow'})
    assert store.name == 'Moscow'