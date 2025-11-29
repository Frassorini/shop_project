from plum import dispatch, overload
from pydantic_extra_types.phone_numbers import PhoneNumber

from shop_project.application.interfaces.interface_account_service import (
    IAccountService,
)
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.subject import Subject, SubjectType
from shop_project.infrastructure.entities.account import Account


class AccountService(IAccountService):
    def create_account(
        self,
        subject: Subject,
        login: str | None = None,
        phone_number: str | None = None,
        email: str | None = None,
    ) -> Account:
        return _create_account(subject, login, phone_number, email)


@overload
def _create_account(
    subject: Customer, login: str | None, phone_number: str | None, email: str | None
) -> Account:
    return Account(
        entity_id=subject.entity_id,
        subject_type=SubjectType.CUSTOMER,
        login=login,
        email=email,
        phone_number=PhoneNumber(phone_number) if phone_number else None,
    )


@overload
def _create_account(
    subject: Employee, login: str | None, phone_number: str | None, email: str | None
) -> Account:
    return Account(
        entity_id=subject.entity_id,
        subject_type=SubjectType.EMPLOYEE,
        login=login,
        email=email,
        phone_number=PhoneNumber(phone_number) if phone_number else None,
    )


@overload
def _create_account(
    subject: Manager, login: str | None, phone_number: str | None, email: str | None
) -> Account:
    return Account(
        entity_id=subject.entity_id,
        subject_type=SubjectType.MANAGER,
        login=login,
        email=email,
        phone_number=PhoneNumber(phone_number) if phone_number else None,
    )


@overload
def _create_account(
    subject: Subject, login: str | None, phone_number: str | None, email: str | None
) -> Account:
    raise NotImplementedError


@dispatch
def _create_account(
    subject: Subject,
    login: str | None,
    phone_number: str | None | None,
    email: str | None,
) -> Account: ...
