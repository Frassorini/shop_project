from dishka import Provider, Scope, alias, provide

from shop_project.application.shared.interfaces.interface_notification import (
    EmailNotificationService,
    SMSNotificationService,
)
from shop_project.infrastructure.notifications.inmemory_email_notification_service import (
    InMemoryEmailNotificationService,
)
from shop_project.infrastructure.notifications.inmemory_sms_notification_service import (
    InMemorySMSNotificationService,
)


class NotificationProvider(Provider):
    scope = Scope.APP

    @provide
    def in_memory_email_notification_service(self) -> InMemoryEmailNotificationService:
        return InMemoryEmailNotificationService()

    @provide
    def in_memory_sms_notification_service(self) -> InMemorySMSNotificationService:
        return InMemorySMSNotificationService()

    email_notification_service_proto = alias(
        InMemoryEmailNotificationService, provides=EmailNotificationService
    )
    sms_notification_service_proto = alias(
        InMemorySMSNotificationService, provides=SMSNotificationService
    )
