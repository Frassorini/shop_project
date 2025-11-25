from abc import ABC
from uuid import UUID

from plum import dispatch, overload
from pydantic import BaseModel

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.authentication.helpers.auth_type import AuthType
from shop_project.infrastructure.authentication.helpers.secret import Secret
from shop_project.infrastructure.authentication.helpers.subject import Subject


class SubjectSecret(PersistableEntity, BaseModel, ABC):
    entity_id: UUID
    auth_type: AuthType
    payload: str


class CustomerSecret(SubjectSecret): ...


class EmployeeSecret(SubjectSecret): ...


class ManagerSecret(SubjectSecret): ...


@overload
def subject_secret_factory(subject: Customer, secret: Secret) -> CustomerSecret:
    return CustomerSecret(
        entity_id=subject.entity_id,
        auth_type=secret.auth_type,
        payload=secret.payload,
    )


@overload
def subject_secret_factory(subject: Employee, secret: Secret) -> EmployeeSecret:
    return EmployeeSecret(
        entity_id=subject.entity_id,
        auth_type=secret.auth_type,
        payload=secret.payload,
    )


@overload
def subject_secret_factory(subject: Manager, secret: Secret) -> ManagerSecret:
    return ManagerSecret(
        entity_id=subject.entity_id, auth_type=secret.auth_type, payload=secret.payload
    )


@dispatch
def subject_secret_factory(subject: Subject, secret: Secret) -> SubjectSecret: ...
