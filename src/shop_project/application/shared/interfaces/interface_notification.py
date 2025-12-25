from typing import Protocol

from shop_project.infrastructure.notifications.messages.email_message import (
    EmailMessage,
)
from shop_project.infrastructure.notifications.messages.sms_message import SMSMessage


class SMSNotificationService(Protocol):
    async def send_sms(self, message: SMSMessage) -> None: ...


class EmailNotificationService(Protocol):
    async def send_email(self, message: EmailMessage) -> None: ...
