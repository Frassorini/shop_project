from typing import Any, Protocol, Self
from uuid import UUID

from plum import dispatch, overload

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.authentication.helpers.auth_type import AuthType
from shop_project.infrastructure.authentication.helpers.secret import Secret
from shop_project.infrastructure.authentication.helpers.subject import Subject


class SubjectSecret(Protocol):
    entity_id: UUID
    auth_type: AuthType
    payload: str


class CustomerSecret(PersistableEntity, SubjectSecret):
    def __init__(self, customer_id: UUID, auth_type: AuthType, payload: str) -> None:
        self.entity_id = customer_id
        self.auth_type = auth_type
        self.payload = payload

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": str(self.entity_id),
            "auth_type": self.auth_type.value,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls.__new__(cls)
        obj.entity_id = snapshot["entity_id"]
        obj.auth_type = AuthType(snapshot["auth_type"])
        obj.payload = snapshot["payload"]
        return obj


class EmployeeSecret(PersistableEntity, SubjectSecret):
    def __init__(self, employee_id: UUID, auth_type: AuthType, payload: str) -> None:
        self.entity_id = employee_id
        self.auth_type = auth_type
        self.payload = payload

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "auth_type": self.auth_type.value,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls.__new__(cls)
        obj.entity_id = snapshot["entity_id"]
        obj.auth_type = AuthType(snapshot["auth_type"])
        obj.payload = snapshot["payload"]
        return obj


class ManagerSecret(PersistableEntity, SubjectSecret):
    def __init__(self, manager_id: UUID, auth_type: AuthType, payload: str) -> None:
        self.entity_id = manager_id
        self.auth_type = auth_type
        self.payload = payload

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "auth_type": self.auth_type.value,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls.__new__(cls)
        obj.entity_id = snapshot["entity_id"]
        obj.auth_type = AuthType(snapshot["auth_type"])
        obj.payload = snapshot["payload"]
        return obj


@overload
def subject_secret_factory(subject: Customer, secret: Secret) -> CustomerSecret:
    return CustomerSecret(
        customer_id=subject.entity_id,
        auth_type=secret.auth_type,
        payload=secret.payload,
    )


@overload
def subject_secret_factory(subject: Employee, secret: Secret) -> EmployeeSecret:
    return EmployeeSecret(
        employee_id=subject.entity_id,
        auth_type=secret.auth_type,
        payload=secret.payload,
    )


@overload
def subject_secret_factory(subject: Manager, secret: Secret) -> ManagerSecret:
    return ManagerSecret(
        manager_id=subject.entity_id, auth_type=secret.auth_type, payload=secret.payload
    )


@dispatch
def subject_secret_factory(subject: Subject, secret: Secret) -> SubjectSecret: ...
