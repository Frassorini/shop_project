from uuid import UUID

from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from shop_project.application.dto.base_dto import BaseDTO


class AccountDTO(BaseDTO):
    entity_id: UUID
    subject_type: str
    login: str | None
    email: EmailStr | None
    phone_number: PhoneNumber | None
