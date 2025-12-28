from datetime import datetime, timedelta, timezone

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.shared.interfaces.interface_totp_service import (
    ITotpService,
)
from shop_project.infrastructure.notifications.inmemory_email_notification_service import (
    InMemoryEmailNotificationService,
)
from shop_project.infrastructure.notifications.inmemory_sms_notification_service import (
    InMemorySMSNotificationService,
)


@pytest.mark.asyncio
async def test_email(async_container: AsyncContainer):
    totp_service = await async_container.get(ITotpService)
    email_service = await async_container.get(InMemoryEmailNotificationService)
    pair = totp_service.create_email_code_message_pair(email="example@example.com")
    await totp_service.send_totp_message(pair.message)
    mesg = await email_service.get_last_message()

    assert mesg
    code = mesg.body.split("Your TOTP code is: ")[1]

    assert not totp_service.verify_totp(pair.totp, "wrong code")

    assert totp_service.verify_totp(pair.totp, code)

    pair.totp.expiration = datetime.now(tz=timezone.utc) - timedelta(days=1)
    assert not totp_service.verify_totp(pair.totp, code)


@pytest.mark.asyncio
async def test_sms(async_container: AsyncContainer):
    totp_service = await async_container.get(ITotpService)
    sms_service = await async_container.get(InMemorySMSNotificationService)
    pair = totp_service.create_sms_code_message_pair(phone_number="+7(999)999-99-99")
    await totp_service.send_totp_message(pair.message)
    mesg = await sms_service.get_last_message()

    assert mesg
    code = mesg.body.split("Your TOTP code is: ")[1]

    assert not totp_service.verify_totp(pair.totp, "wrong code")

    assert totp_service.verify_totp(pair.totp, code)

    pair.totp.expiration = datetime.now(tz=timezone.utc) - timedelta(days=1)
    assert not totp_service.verify_totp(pair.totp, code)
