from typing import Protocol

from pydantic import EmailStr

from shop_project.domain.interfaces.subject import Subject
from shop_project.infrastructure.entities.account import Account


class IAccountService(Protocol):
    def set_password(self, account: Account, password: str) -> None: ...

    def verify_password(self, account: Account, password: str) -> bool: ...

    def create_account(
        self,
        subject: Subject,
        login: str | None = None,
        phone_number: str | None = None,
        email: EmailStr | None = None,
    ) -> Account: ...
