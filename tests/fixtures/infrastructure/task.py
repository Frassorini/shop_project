from typing import Callable
from uuid import uuid4

import pytest
from dishka.container import Container

from shop_project.infrastructure.authentication.services.session_service import (
    SessionService,
)
from shop_project.infrastructure.entities.task import Task
from tests.helpers import AggregateContainer


@pytest.fixture
def task_container_factory(
    domain_container: Container,
) -> Callable[..., AggregateContainer]:

    def fact() -> AggregateContainer:
        session_service = domain_container.get(SessionService)

        application_task = Task(
            entity_id=uuid4(),
            handler="test_handler",
            params_json="{}",
        )

        return AggregateContainer(aggregate=application_task, dependencies={})

    return fact
