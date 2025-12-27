from typing import Any, Self
from uuid import UUID

from pydantic import EmailStr, SecretStr

from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.subject import SubjectEnum
from shop_project.shared.phone_str import PhoneStr


class Account(PersistableEntity):
    def __init__(
        self,
        entity_id: UUID,
        subject_type: SubjectEnum,
        password_verifier: SecretStr | None,
        login: str | None,
        email: EmailStr | None,
        phone_number: PhoneStr | None,
    ) -> None:
        self.entity_id: UUID = entity_id
        self.subject_type: SubjectEnum = subject_type
        self.password_verifier: SecretStr | None = password_verifier
        self.login: str | None = login
        self.email: EmailStr | None = email
        self.phone_number: PhoneStr | None = phone_number

    def __post_init__(self) -> None:
        if not self.login and not self.email and not self.phone_number:
            raise ValueError("Phone or email or login must be provided")
        if self.login and not self.password_verifier:
            raise ValueError("Password must be provided")

    @classmethod
    def load(
        cls,
        entity_id: UUID,
        subject_type: SubjectEnum,
        password_verifier: SecretStr | None,
        login: str | None,
        phone_number: str | None,
        email: str | None,
        **kw: Any,
    ) -> Self:
        obj = cls(
            entity_id=entity_id,
            subject_type=subject_type,
            password_verifier=password_verifier,
            login=login,
            email=email,
            phone_number=phone_number,
        )

        obj.__post_init__()

        return obj
