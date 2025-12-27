from typing import Protocol

from pydantic import EmailStr

from shop_project.application.entities.account import Account
from shop_project.domain.interfaces.subject import Subject


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
