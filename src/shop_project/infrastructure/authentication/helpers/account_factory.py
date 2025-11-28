from plum import dispatch, overload

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.infrastructure.authentication.helpers.subject_type_union import (
    SubjectTypeUnion,
)
from shop_project.infrastructure.entities.account import Account, SubjectType


@overload
def create_account(subject: Customer) -> Account:
    return Account(
        subject_id=subject.entity_id,
        subject_type=SubjectType.CUSTOMER,
    )


@overload
def create_account(subject: Employee) -> Account:
    return Account(
        subject_id=subject.entity_id,
        subject_type=SubjectType.EMPLOYEE,
    )


@overload
def create_account(subject: Manager) -> Account:
    return Account(
        subject_id=subject.entity_id,
        subject_type=SubjectType.MANAGER,
    )


@overload
def create_account(subject: SubjectTypeUnion) -> Account:
    raise NotImplementedError


@dispatch
def create_account(subject: SubjectTypeUnion) -> Account: ...
