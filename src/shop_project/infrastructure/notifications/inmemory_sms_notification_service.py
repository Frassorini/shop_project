from shop_project.application.shared.interfaces.interface_notification import (
    SMSNotificationService,
)
from shop_project.infrastructure.notifications.messages.sms_message import SMSMessage


class InMemorySMSNotificationService(SMSNotificationService):
    def __init__(self) -> None:
        self.messages: list[SMSMessage] = []

    async def send_sms(self, message: SMSMessage) -> None:
        self.messages.append(message)

    async def get_last_message(self) -> SMSMessage | None:
        if not self.messages:
            return None
        return self.messages[-1]
