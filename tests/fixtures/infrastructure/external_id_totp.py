from typing import Callable
from uuid import UUID

import pytest
from dishka.container import Container

from shop_project.application.shared.interfaces.interface_totp_service import (
    ITotpService,
)
from shop_project.infrastructure.entities.external_id_totp import ExternalIdTotp
from tests.helpers import AggregateContainer


@pytest.fixture
def external_id_totp(
    unique_id_factory: Callable[[], UUID],
    domain_container: Container,
) -> Callable[[], ExternalIdTotp]:
    def fact() -> ExternalIdTotp:
        totp_service = domain_container.get(ITotpService)

        pair = totp_service.create_email_code_message_pair(email="example@example.com")

        return pair.totp

    return fact


@pytest.fixture
def external_id_totp_container_factory(
    external_id_totp: Callable[[], ExternalIdTotp],
) -> Callable[..., AggregateContainer]:

    def fact() -> AggregateContainer:
        return AggregateContainer(aggregate=external_id_totp(), dependencies={})

    return fact
