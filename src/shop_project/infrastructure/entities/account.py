from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel, EmailStr, SecretStr

from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.subject import SubjectEnum
from shop_project.shared.phone_str import PhoneStr


class Account(PersistableEntity, BaseModel):
    entity_id: UUID
    subject_type: SubjectEnum
    password_verifier: SecretStr | None
    login: str | None
    email: EmailStr | None
    phone_number: PhoneStr | None

    def __post_init__(self) -> None:
        if not self.login and not self.email and not self.phone_number:
            raise ValueError("Phone or email or login must be provided")

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
