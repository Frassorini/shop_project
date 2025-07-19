from shop_project.shared.entity_id import EntityId
from shop_project.shared.identity_mixin import IdentityMixin


class ExampleDomainClass1(IdentityMixin):
    def __init__(self, entity_id: EntityId) -> None:
        self._entity_id: EntityId = entity_id
class ExampleDomainClass2(IdentityMixin):
    def __init__(self, entity_id: EntityId) -> None:
        self._entity_id: EntityId = entity_id


def test_not_eq_different_classes() -> None:
    obj_1 = ExampleDomainClass1(EntityId('1'))
    
    obj_2 = ExampleDomainClass2(EntityId('1'))
    
    assert obj_1 != obj_2


def test_eq() -> None:
    obj_1 = ExampleDomainClass1(EntityId('1'))
    
    obj_2 = ExampleDomainClass1(EntityId('1'))
    
    assert obj_1 == obj_2


def test_not_eq() -> None:
    obj_1 = ExampleDomainClass1(EntityId('1'))
    
    obj_2 = ExampleDomainClass1(EntityId('2'))
    
    assert obj_1 != obj_2