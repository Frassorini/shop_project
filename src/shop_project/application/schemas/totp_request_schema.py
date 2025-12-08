from abc import ABC
from typing import Any

from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from shop_project.application.schemas.base_schema import BaseSchema


class TotpRequestSchema(BaseSchema, ABC):
    identifier: Any


class EmailTotpRequestSchema(TotpRequestSchema):
    identifier: EmailStr


class SmsTotpRequestSchema(TotpRequestSchema):
    identifier: PhoneNumber
