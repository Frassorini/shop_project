from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator, Callable, Never

import pytest
import pytest_asyncio
from dishka import make_async_container, make_container
from dishka.async_container import AsyncContainer
from dishka.container import Container
from pydantic import SecretBytes
from taskiq import AsyncBroker

from shop_project.infrastructure.dependency_injection.application.application_task_handler_provider import (
    ApplicationTaskHandlerProvider,
)
from shop_project.infrastructure.dependency_injection.application.auth_application_provider import (
    AuthApplicationProvider,
)
from shop_project.infrastructure.dependency_injection.application.customer_application_provider import (
    CustomerApplicationProvider,
)
from shop_project.infrastructure.dependency_injection.application.employee_application_provider import (
    EmployeeApplicationProvider,
)
from shop_project.infrastructure.dependency_injection.application.manager_application_provider import (
    ManagerApplicationProvider,
)
from shop_project.infrastructure.dependency_injection.application.payment_application_provider import (
    PaymentApplicationProvider,
)
from shop_project.infrastructure.dependency_injection.application.policy_provider import (
    PolicyProvider,
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
from shop_project.infrastructure.dependency_injection.infrastructure.notification_provider import (
    NotificationProvider,
)
from shop_project.infrastructure.dependency_injection.infrastructure.payment_provider import (
    PaymentProvider,
)
from shop_project.infrastructure.dependency_injection.infrastructure.persistence_provider import (
    PersistenceProvider,
)
from shop_project.infrastructure.persistence.database.core import Database
from tests.helpers import get_test_jwt_private_key, get_test_jwt_public_key


@pytest.fixture(scope="session")
def domain_container() -> Container:
    container = make_container(
        DomainProvider(),
        CryptographyProvider(
            JwtKeyContainer(
                public_key=SecretBytes(get_test_jwt_public_key()),
                private_key=SecretBytes(get_test_jwt_private_key()),
            )
        ),
        PaymentProvider(),
        AuthenticationProvider(),
        NotificationProvider(),
    )

    return container


@pytest_asyncio.fixture(scope="session")
async def base_async_container() -> AsyncContainer:
    def null_ctx() -> Never:
        raise RuntimeError("Null dependency context access attempted")

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
        PersistenceProvider(null_ctx),
        BrokerProvider(null_ctx),
        AuthApplicationProvider(),
        CustomerApplicationProvider(),
        ManagerApplicationProvider(),
        EmployeeApplicationProvider(),
        PaymentApplicationProvider(),
        PolicyProvider(),
        ApplicationTaskHandlerProvider(),
        NotificationProvider(),
    )

    return container


@pytest_asyncio.fixture
async def async_container(
    test_db_factory: Callable[[], AbstractAsyncContextManager[Database]],
    test_broker_container_factory: Callable[
        [], AbstractAsyncContextManager[AsyncBroker]
    ],
    setup_broker: Callable[[AsyncBroker, AsyncContainer], None],
    base_async_container: AsyncContainer,
) -> AsyncGenerator[AsyncContainer, None]:
    container = base_async_container

    async with test_db_factory() as db:
        async with test_broker_container_factory() as broker:
            async with base_async_container(
                context={
                    Database: db,
                    AsyncBroker: broker,
                }
            ) as ct:
                setup_broker(await ct.get(AsyncBroker), ct)
                yield ct

    await container.close()
