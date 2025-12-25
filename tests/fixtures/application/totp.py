from typing import Awaitable, Callable

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.authentication.commands.totp_challenge_service import (
    TotpChallengeService,
)
from shop_project.application.authentication.schemas.totp_request_schema import (
    EmailTotpRequestSchema,
    SmsTotpRequestSchema,
)
from shop_project.infrastructure.notifications.inmemory_email_notification_service import (
    InMemoryEmailNotificationService,
)
from shop_project.infrastructure.notifications.inmemory_sms_notification_service import (
    InMemorySMSNotificationService,
)


@pytest.fixture
def totp_sms(
    async_container: AsyncContainer,
) -> Callable[[str], Awaitable[str]]:
    async def _inner(
        phone_number: str,
    ) -> str:
        totp_challenge_service = await async_container.get(TotpChallengeService)
        sms_service = await async_container.get(InMemorySMSNotificationService)

        totp_request = SmsTotpRequestSchema(identifier=phone_number)

        await totp_challenge_service.begin_sms_challenge(totp_request)

        mesg = await sms_service.get_last_message()
        assert mesg
        code = mesg.body.split("Your TOTP code is: ")[1]
        return code

    return _inner


@pytest.fixture
def totp_email(
    async_container: AsyncContainer,
) -> Callable[[str], Awaitable[str]]:
    async def _inner(
        email: str,
    ) -> str:
        totp_challenge_service = await async_container.get(TotpChallengeService)
        email_service = await async_container.get(InMemoryEmailNotificationService)

        totp_request = EmailTotpRequestSchema(identifier=email)

        await totp_challenge_service.begin_email_challenge(totp_request)

        mesg = await email_service.get_last_message()
        assert mesg
        code = mesg.body.split("Your TOTP code is: ")[1]
        return code

    return _inner
