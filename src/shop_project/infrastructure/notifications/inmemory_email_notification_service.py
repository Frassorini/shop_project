from shop_project.application.shared.interfaces.interface_notification import (
    EmailNotificationService,
)
from shop_project.infrastructure.notifications.messages.email_message import (
    EmailMessage,
)


class InMemoryEmailNotificationService(EmailNotificationService):
    def __init__(self) -> None:
        self.messages: list[EmailMessage] = []

    async def send_email(self, message: EmailMessage) -> None:
        self.messages.append(message)

    async def get_last_message(self) -> EmailMessage | None:
        if not self.messages:
            return None
        return self.messages[-1]
