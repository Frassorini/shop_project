from typing import Self
from uuid import UUID

from pydantic import EmailStr, SecretStr

from shop_project.application.dto.base_dto import BaseDTO
from shop_project.domain.interfaces.subject import SubjectEnum
from shop_project.infrastructure.entities.account import Account
from shop_project.shared.phone_str import PhoneStr


class AccountDTO(BaseDTO[Account]):
    entity_id: UUID
    subject_type: str
    password_verifier: SecretStr | None
    login: str | None
    email: EmailStr | None
    phone_number: PhoneStr | None

    @classmethod
    def to_dto(cls, domain_object: Account) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            subject_type=domain_object.subject_type.value,
            password_verifier=domain_object.password_verifier,
            login=domain_object.login,
            email=domain_object.email,
            phone_number=domain_object.phone_number,
        )

    def to_domain(self) -> Account:
        return Account.load(
            entity_id=self.entity_id,
            subject_type=SubjectEnum(self.subject_type),
            password_verifier=self.password_verifier,
            login=self.login,
            email=self.email,
            phone_number=self.phone_number,
        )
