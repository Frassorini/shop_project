from pydantic import EmailStr

from shop_project.infrastructure.notifications.messages.message import (
    NotificationMessage,
)


class EmailMessage(NotificationMessage):
    from_email: EmailStr
    to_email: EmailStr
    subject: str
    body: str
