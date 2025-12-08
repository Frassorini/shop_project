from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator, Callable

import pytest
import pytest_asyncio
from dishka import make_async_container, make_container
from dishka.async_container import AsyncContainer
from dishka.container import Container
from pydantic import SecretBytes

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.dependency_injection.application.application_service_provider import (
    ApplicationServiceProvider,
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
from shop_project.infrastructure.message_broker.broker_container import BrokerContainer
from tests.helpers import get_test_jwt_private_key, get_test_jwt_public_key


@pytest.fixture()
def domain_container() -> Container:
    container = make_container(
        DomainProvider(),
        CryptographyProvider(
            JwtKeyContainer(
                public_key=SecretBytes(get_test_jwt_public_key()),
                private_key=SecretBytes(get_test_jwt_private_key()),
            )
        ),
        AuthenticationProvider(),
        NotificationProvider(),
    )

    return container


@pytest_asyncio.fixture()
async def async_container(
    test_db_factory: Callable[[], AbstractAsyncContextManager[Database]],
    test_broker_container_factory: Callable[
        [], AbstractAsyncContextManager[BrokerContainer]
    ],
) -> AsyncGenerator[AsyncContainer, None]:
    container = make_async_container(
        DomainProvider(),
        CryptographyProvider(
            JwtKeyContainer(
                public_key=SecretBytes(get_test_jwt_public_key()),
                private_key=SecretBytes(get_test_jwt_private_key()),
            )
        ),
        AuthenticationProvider(),
        DatabaseProvider(test_db_factory),
        BrokerProvider(test_broker_container_factory),
        ApplicationServiceProvider(),
        NotificationProvider(),
    )

    async with container() as ct:
        yield ct

    await container.close()
