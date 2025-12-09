from shop_project.infrastructure.notifications.messages.message import (
    NotificationMessage,
)
from shop_project.shared.phone_str import PhoneStr


class SMSMessage(NotificationMessage):
    from_number: PhoneStr
    to_number: PhoneStr
    body: str
