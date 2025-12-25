from plum import dispatch, overload
from pydantic import SecretStr

from shop_project.application.shared.interfaces.interface_account_service import (
    IAccountService,
)
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.subject import Subject, SubjectEnum
from shop_project.infrastructure.authentication.exceptions import AuthException
from shop_project.infrastructure.cryptography.interfaces.password_hasher import (
    PasswordHasher,
)
from shop_project.infrastructure.entities.account import Account


class AccountService(IAccountService):
    def __init__(self, password_hasher: PasswordHasher) -> None:
        self.password_hasher: PasswordHasher = password_hasher

    def set_password(self, account: Account, password: str) -> None:
        account.password_verifier = SecretStr(self.password_hasher.hash(password))

    def verify_password(self, account: Account, password: str) -> bool:
        if not account.password_verifier:
            raise AuthException("Account has no password")

        return self.password_hasher.verify(
            password, account.password_verifier.get_secret_value()
        )

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
        subject_type=SubjectEnum.CUSTOMER,
        password_verifier=None,
        login=login,
        email=email,
        phone_number=phone_number,
    )


@overload
def _create_account(
    subject: Employee, login: str | None, phone_number: str | None, email: str | None
) -> Account:
    return Account(
        entity_id=subject.entity_id,
        subject_type=SubjectEnum.EMPLOYEE,
        password_verifier=None,
        login=login,
        email=email,
        phone_number=phone_number,
    )


@overload
def _create_account(
    subject: Manager, login: str | None, phone_number: str | None, email: str | None
) -> Account:
    return Account(
        entity_id=subject.entity_id,
        subject_type=SubjectEnum.MANAGER,
        password_verifier=None,
        login=login,
        email=email,
        phone_number=phone_number,
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
