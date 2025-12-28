from datetime import datetime, timedelta, timezone
from typing import Coroutine
from uuid import uuid4

from plum import dispatch, overload
from pydantic import SecretStr

from shop_project.application.entities.external_id_totp import ExternalIdTotp
from shop_project.application.shared.interfaces.interface_notification import (
    EmailNotificationService,
    SMSNotificationService,
)
from shop_project.application.shared.interfaces.interface_totp_service import (
    CodeMessagePair,
    ITotpService,
)
from shop_project.infrastructure.cryptography.interfaces.code_generator import (
    CodeGenerator,
)
from shop_project.infrastructure.cryptography.interfaces.password_hasher import (
    PasswordHasher,
)
from shop_project.infrastructure.notifications.messages.email_message import (
    EmailMessage,
)
from shop_project.infrastructure.notifications.messages.message import (
    NotificationMessage,
)
from shop_project.infrastructure.notifications.messages.sms_message import SMSMessage


class TotpService(ITotpService):
    def __init__(
        self,
        password_hasher: PasswordHasher,
        code_generator: CodeGenerator,
        email_notfication_service: EmailNotificationService,
        sms_notfication_service: SMSNotificationService,
        totp_ttl: timedelta,
        email_sender: str,
        sms_sender: str,
    ) -> None:
        self._password_hasher = password_hasher
        self._code_generator = code_generator
        self._email_notfication_service = email_notfication_service
        self._sms_notfication_service = sms_notfication_service
        self._totp_ttl = totp_ttl
        self._email_sender = email_sender
        self._sms_sender = sms_sender

    def verify_totp(self, totp: ExternalIdTotp, code: str) -> bool:
        if totp.expiration < datetime.now(tz=timezone.utc):
            return False

        return self._password_hasher.verify(code, totp.totp_verifier.get_secret_value())

    def create_email_code_message_pair(self, email: str) -> CodeMessagePair:
        code = self._code_generator.generate()
        totp = self._create_totp(
            external_id_type="email", external_id=email, totp_secret=code
        )
        message = self._create_email_message(email=email, code=code)
        return CodeMessagePair(totp=totp, message=message)

    def create_sms_code_message_pair(self, phone_number: str) -> CodeMessagePair:
        code = self._code_generator.generate()
        totp = self._create_totp(
            external_id_type="phone_number", external_id=phone_number, totp_secret=code
        )
        message = self._create_sms_message(phone_number=phone_number, code=code)
        return CodeMessagePair(totp=totp, message=message)

    async def send_totp_message(self, message: NotificationMessage) -> None:
        await self._send_totp_message(message)

    @overload
    def _send_totp_message(self, message: SMSMessage) -> Coroutine[None, None, None]:
        return self._sms_notfication_service.send_sms(message)

    @overload
    def _send_totp_message(self, message: EmailMessage) -> Coroutine[None, None, None]:
        return self._email_notfication_service.send_email(message)

    @overload
    def _send_totp_message(
        self, message: NotificationMessage
    ) -> Coroutine[None, None, None]:
        raise NotImplementedError

    @dispatch
    def _send_totp_message(
        self, message: NotificationMessage
    ) -> Coroutine[None, None, None]: ...

    def _create_sms_message(self, phone_number: str, code: str) -> SMSMessage:
        return SMSMessage(
            from_number=self._sms_sender,
            to_number=phone_number,
            body=f"Your TOTP code is: {code}",
        )

    def _create_email_message(self, email: str, code: str) -> EmailMessage:
        return EmailMessage(
            from_email=self._email_sender,
            to_email=email,
            subject="TOTP code",
            body=f"Your TOTP code is: {code}",
        )

    def _create_totp(
        self, external_id_type: str, external_id: str, totp_secret: str
    ) -> ExternalIdTotp:
        return ExternalIdTotp(
            entity_id=uuid4(),
            external_id_type=external_id_type,
            external_id=external_id,
            totp_verifier=SecretStr(self._password_hasher.hash(totp_secret)),
            issued_at=datetime.now(tz=timezone.utc),
            expiration=datetime.now(tz=timezone.utc) + self._totp_ttl,
        )
