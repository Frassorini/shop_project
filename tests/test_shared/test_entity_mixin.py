from uuid import UUID, uuid4

from shop_project.shared.entity_id import EntityId
from shop_project.shared.identity_mixin import IdentityMixin


class ExampleDomainClass1(IdentityMixin):
    def __init__(self, entity_id: EntityId) -> None:
        self._entity_id: EntityId = entity_id
class ExampleDomainClass2(IdentityMixin):
    def __init__(self, entity_id: EntityId) -> None:
        self._entity_id: EntityId = entity_id


def test_not_eq_different_classes() -> None:
    uuid_id = uuid4()
    
    obj_1 = ExampleDomainClass1(EntityId(uuid_id))
    
    obj_2 = ExampleDomainClass2(EntityId(uuid_id))
    
    assert obj_1 != obj_2


def test_eq() -> None:
    uuid_id = uuid4()
    
    obj_1 = ExampleDomainClass1(EntityId(uuid_id))
    
    obj_2 = ExampleDomainClass1(EntityId(uuid_id))
    
    assert obj_1 == obj_2


def test_not_eq() -> None:
    uuid_id_1 = uuid4()
    uuid_id_2 = uuid4()
    
    obj_1 = ExampleDomainClass1(EntityId(uuid_id_1))
    
    obj_2 = ExampleDomainClass1(EntityId(uuid_id_2))
    
    assert obj_1 != obj_2