from dataclasses import dataclass

from shop_project.application.entities.external_id_totp import ExternalIdTotp
from shop_project.infrastructure.notifications.messages.email_message import (
    EmailMessage,
)
from shop_project.infrastructure.notifications.messages.message import (
    NotificationMessage,
)
from shop_project.infrastructure.notifications.messages.sms_message import SMSMessage


@dataclass(frozen=True)
class CodeMessagePair:
    totp: ExternalIdTotp
    message: EmailMessage | SMSMessage


class ITotpService:
    def verify_totp(self, totp: ExternalIdTotp, code: str) -> bool: ...

    def create_email_code_message_pair(self, email: str) -> CodeMessagePair: ...

    def create_sms_code_message_pair(self, phone_number: str) -> CodeMessagePair: ...

    async def send_totp_message(self, message: NotificationMessage) -> None: ...
