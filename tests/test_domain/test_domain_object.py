import pytest

from domain.exceptions import DomainException
from domain.domain_object import DomainObject


class ExampleDomainClass1(DomainObject):
        pass
class ExampleDomainClass2(DomainObject):
        pass


def test_raise_id_redefinition() -> None:
    obj = ExampleDomainClass1()
    obj.id_ = 1
    
    with pytest.raises(DomainException):
        obj.id_ = 2


def test_not_eq_differenet_classes() -> None:
    obj_1 = ExampleDomainClass1()
    obj_1.id_ = 1
    
    obj_2 = ExampleDomainClass2()
    obj_2.id_ = 1
    
    assert obj_1 != obj_2


def get_obj(id_: int|None=None) -> object:
    obj = ExampleDomainClass1()
    if id_ is not None:
        obj.id_ = id_
    return obj

@pytest.mark.parametrize(
    "obj_1, obj_2, exc",
    [
        (get_obj(), get_obj(), DomainException),
        (get_obj(), get_obj(1), DomainException),
        (get_obj(1), get_obj(), DomainException),
        (get_obj(1), get_obj(1), None),
        
    ]
)
def test_id_(obj_1: object, obj_2: object, exc: type[Exception] | None) -> None:
    if exc:
        with pytest.raises(exc):
            _ = obj_1 == obj_2
    else:
        assert obj_1 == obj_2