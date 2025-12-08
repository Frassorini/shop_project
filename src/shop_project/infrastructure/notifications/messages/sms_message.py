from pydantic_extra_types.phone_numbers import PhoneNumber

from shop_project.infrastructure.notifications.messages.message import (
    NotificationMessage,
)


class SMSMessage(NotificationMessage):
    from_number: PhoneNumber
    to_number: PhoneNumber
    body: str
