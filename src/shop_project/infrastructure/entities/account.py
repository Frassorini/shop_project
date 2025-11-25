from enum import Enum
from typing import Self
from uuid import UUID

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class SubjectType(Enum):
    CUSTOMER = "CUSTOMER"
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"


class Account(PersistableEntity):
    entity_id: UUID
    subject_type: SubjectType

    def __init__(self, subject_id: UUID, subject_type: SubjectType) -> None:
        self.entity_id = subject_id
        self.subject_type = subject_type

    @classmethod
    def _load(cls, entity_id: UUID, subject_type: SubjectType) -> Self:
        obj = cls.__new__(cls)

        obj.entity_id = entity_id
        obj.subject_type = subject_type

        return obj
