from abc import ABC
from typing import Any

from pydantic import EmailStr, SecretStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from shop_project.application.schemas.base_schema import BaseSchema


class CredentialSchema(BaseSchema, ABC):
    identifier: Any
    plaintext_secret: SecretStr


class EmailCredentialSchema(CredentialSchema):
    identifier: EmailStr


class PhoneCredentialSchema(CredentialSchema):
    identifier: PhoneNumber


class LoginCredentialSchema(CredentialSchema):
    identifier: str
