from typing import TYPE_CHECKING, Annotated, Union

import phonenumbers
from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumberValidator

if TYPE_CHECKING:
    PhoneStr = str
else:
    PhoneStr = Annotated[
        Union[str, phonenumbers.PhoneNumber],
        PhoneNumberValidator(number_format="RFC3966"),
    ]


class _PhoneModel(BaseModel):
    phone_number: PhoneStr


def validate_phone_number(value: str) -> str:
    return _PhoneModel(phone_number=value).phone_number
