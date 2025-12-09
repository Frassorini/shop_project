from uuid import UUID

from pydantic import EmailStr, SecretStr

from shop_project.application.dto.base_dto import BaseDTO
from shop_project.shared.phone_str import PhoneStr


class AccountDTO(BaseDTO):
    entity_id: UUID
    subject_type: str
    password_verifier: SecretStr | None
    login: str | None
    email: EmailStr | None
    phone_number: PhoneStr | None
