from typing import Awaitable, Callable, Sequence, Type
from uuid import uuid4

import pytest
from dishka.container import Container

from shop_project.application.entities.operation_log.operation_log import (
    OperationLog,
    create_operation_log,
)
from shop_project.application.entities.operation_log.operation_log_payload_implementations.employee import (
    CreateEmployeeOperationLogPayload,
)
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.subject import SubjectEnum
from shop_project.infrastructure.authentication.services.session_service import (
    SessionService,
)
from tests.helpers import AggregateContainer


@pytest.fixture
def operation_log_container_factory(
    domain_container: Container,
) -> Callable[..., AggregateContainer]:
    def fact() -> AggregateContainer:
        session_service = domain_container.get(SessionService)

        operation_log = create_operation_log(
            payload=CreateEmployeeOperationLogPayload(
                subject_type=SubjectEnum.MANAGER,
                subject_id=uuid4(),
                employee_name="John Doe",
                employee_id=uuid4(),
            )
        )

        return AggregateContainer(aggregate=operation_log, dependencies={})

    return fact


@pytest.fixture
def ensure_operation_log_amount(
    uow_get_all_single_model: Callable[
        [Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]
    ],
) -> Callable[[int], Awaitable[Sequence[OperationLog]]]:
    async def _inner(amount: int) -> Sequence[OperationLog]:
        logs: Sequence[OperationLog] = await uow_get_all_single_model(
            OperationLog
        )  # pyright: ignore[reportAssignmentType]
        if not len(logs) == amount:
            raise RuntimeError("Operation logs amount does not match")
        return logs

    return _inner
