from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.subject import SubjectType


class Account(PersistableEntity, BaseModel):
    entity_id: UUID
    subject_type: SubjectType
    login: str | None
    email: EmailStr | None
    phone_number: PhoneNumber | None

    def __post_init__(self) -> None:
        if not self.login and not self.email and not self.phone_number:
            raise ValueError("Phone or email or login must be provided")

    @classmethod
    def _load(
        cls,
        entity_id: UUID,
        subject_type: SubjectType,
        login: str | None,
        phone: PhoneNumber | None,
        email: EmailStr | None,
        **kw: Any,
    ) -> Self:
        obj = cls(
            entity_id=entity_id,
            subject_type=subject_type,
            login=login,
            email=email,
            phone_number=phone,
        )

        obj.__post_init__()

        return obj
