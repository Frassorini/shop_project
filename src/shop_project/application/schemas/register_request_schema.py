from abc import ABC
from typing import Any

from pydantic import EmailStr, SecretStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from shop_project.application.schemas.base_schema import BaseSchema


class RegisterRequestSchema(BaseSchema, ABC):
    identifier: Any
    credential: SecretStr


class EmailRegisterRequestSchema(RegisterRequestSchema):
    identifier: EmailStr


class PhoneRegisterRequestSchema(RegisterRequestSchema):
    identifier: PhoneNumber


class LoginRegisterRequestSchema(RegisterRequestSchema):
    identifier: str
