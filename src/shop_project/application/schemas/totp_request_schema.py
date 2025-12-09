from abc import ABC
from typing import Any

from pydantic import EmailStr

from shop_project.application.schemas.base_schema import BaseSchema
from shop_project.shared.phone_str import PhoneStr


class TotpRequestSchema(BaseSchema, ABC):
    identifier: Any


class EmailTotpRequestSchema(TotpRequestSchema):
    identifier: EmailStr


class SmsTotpRequestSchema(TotpRequestSchema):
    identifier: PhoneStr
