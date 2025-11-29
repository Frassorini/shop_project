from abc import ABC
from enum import Enum

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class SubjectType(Enum):
    CUSTOMER = "CUSTOMER"
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"


class Subject(PersistableEntity, ABC):
    name: str
