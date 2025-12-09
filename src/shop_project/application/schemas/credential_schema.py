from abc import ABC
from typing import Any

from pydantic import EmailStr, SecretStr

from shop_project.application.schemas.base_schema import BaseSchema
from shop_project.shared.phone_str import PhoneStr


class CredentialSchema(BaseSchema, ABC):
    identifier: Any


class TotpCredentialSchema(CredentialSchema):
    code_plaintext: SecretStr


class PasswordCredentialSchema(CredentialSchema):
    password_plaintext: SecretStr


class EmailTotpCredentialSchema(TotpCredentialSchema):
    identifier: EmailStr


class PhoneTotpCredentialSchema(TotpCredentialSchema):
    identifier: PhoneStr


class EmailPasswordCredentialSchema(PasswordCredentialSchema):
    identifier: EmailStr


class PhonePasswordCredentialSchema(PasswordCredentialSchema):
    identifier: PhoneStr


class LoginPasswordCredentialSchema(PasswordCredentialSchema):
    identifier: str
