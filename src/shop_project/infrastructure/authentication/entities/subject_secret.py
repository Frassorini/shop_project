from typing import Any, Protocol, Self

from plum import dispatch, overload

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.authentication.helpers.auth_type import AuthType
from shop_project.infrastructure.authentication.helpers.secret import Secret
from shop_project.infrastructure.authentication.helpers.subject import Subject
from shop_project.shared.entity_id import EntityId


class SubjectSecret(Protocol):
    auth_type: AuthType
    payload: str

    @property
    def entity_id(self) -> EntityId: ...


class CustomerSecret(PersistableEntity, SubjectSecret):
    def __init__(
        self, customer_id: EntityId, auth_type: AuthType, payload: str
    ) -> None:
        self._entity_id = customer_id
        self.auth_type = auth_type
        self.payload = payload

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": str(self._entity_id.value),
            "auth_type": self.auth_type.value,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls.__new__(cls)
        obj._entity_id = EntityId(snapshot["entity_id"])
        obj.auth_type = AuthType(snapshot["auth_type"])
        obj.payload = snapshot["payload"]
        return obj


class EmployeeSecret(PersistableEntity, SubjectSecret):
    def __init__(
        self, employee_id: EntityId, auth_type: AuthType, payload: str
    ) -> None:
        self._entity_id = employee_id
        self.auth_type = auth_type
        self.payload = payload

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self._entity_id.value,
            "auth_type": self.auth_type.value,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls.__new__(cls)
        obj._entity_id = EntityId(snapshot["entity_id"])
        obj.auth_type = AuthType(snapshot["auth_type"])
        obj.payload = snapshot["payload"]
        return obj


class ManagerSecret(PersistableEntity, SubjectSecret):
    def __init__(self, manager_id: EntityId, auth_type: AuthType, payload: str) -> None:
        self._entity_id = manager_id
        self.auth_type = auth_type
        self.payload = payload

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self._entity_id.value,
            "auth_type": self.auth_type.value,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls.__new__(cls)
        obj._entity_id = EntityId(snapshot["entity_id"])
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
