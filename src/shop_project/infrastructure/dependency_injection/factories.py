from dishka import make_async_container
from dishka.async_container import AsyncContainer
from pydantic import SecretBytes
from taskiq import AsyncBroker

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.dependency_injection.application.application_service_provider import (
    ApplicationServiceProvider,
)
from shop_project.infrastructure.dependency_injection.application.application_task_handler_provider import (
    ApplicationTaskHandlerProvider,
)
from shop_project.infrastructure.dependency_injection.domain.domain_provider import (
    DomainProvider,
)
from shop_project.infrastructure.dependency_injection.infrastructure.authentication_provider import (
    AuthenticationProvider,
)
from shop_project.infrastructure.dependency_injection.infrastructure.broker_provider import (
    BrokerProvider,
)
from shop_project.infrastructure.dependency_injection.infrastructure.cryptography_provider import (
    CryptographyProvider,
    JwtKeyContainer,
)
from shop_project.infrastructure.dependency_injection.infrastructure.database_provider import (
    DatabaseProvider,
)
from shop_project.infrastructure.dependency_injection.infrastructure.notification_provider import (
    NotificationProvider,
)
from shop_project.infrastructure.dependency_injection.infrastructure.payment_provider import (
    PaymentProvider,
)
from shop_project.shared.create_context import create_context_from_value
from tests.helpers import get_test_jwt_private_key, get_test_jwt_public_key


def container_taskiq_worker_factory(broker: AsyncBroker) -> AsyncContainer:
    broker_ctx = create_context_from_value(broker)
    database_ctx = create_context_from_value(Database.from_env())

    container = make_async_container(
        DomainProvider(),
        CryptographyProvider(
            JwtKeyContainer(
                public_key=SecretBytes(get_test_jwt_public_key()),
                private_key=SecretBytes(get_test_jwt_private_key()),
            )
        ),
        PaymentProvider(),
        AuthenticationProvider(),
        DatabaseProvider(database_ctx),
        BrokerProvider(broker_ctx),
        ApplicationServiceProvider(),
        ApplicationTaskHandlerProvider(),
        NotificationProvider(),
    )

    return container
