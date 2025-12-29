from decimal import Decimal
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Sequence,
    Type,
)
from uuid import uuid4

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.entities.operation_log.operation_code import (
    OperationCodeEnum,
)
from shop_project.application.entities.operation_log.operation_log import OperationLog
from shop_project.application.entities.operation_log.operation_log_payload_implementations.purchase import (
    AutoUnclaimPurchaseOperationLogPayload,
    CancelPurchaseOperationLogPayload,
    RefundPurchaseOperationLogPayload,
)
from shop_project.application.manager.queries.operation_log_read_service import (
    OperationLogReadService,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.scenarios.operation_log import log_operation
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.subject import Subject
from shop_project.infrastructure.persistence.query.query_builder import QueryBuilder
from shop_project.infrastructure.persistence.unit_of_work import UnitOfWorkFactory
from tests.helpers import AggregateContainer


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_operation_log_read_service_read_by_sequence(
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    uow_factory: UnitOfWorkFactory,
    async_container: AsyncContainer,
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    manager_container_factory: Callable[[], AggregateContainer],
    employee_container_factory: Callable[[], AggregateContainer],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
    ensure_operation_log_amount: Callable[[int], Awaitable[Sequence[OperationLog]]],
) -> None:
    operation_log_service = await async_container.get(OperationLogReadService)
    manager_container = manager_container_factory()
    manager: Manager = (
        manager_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_payload = await get_subject_access_token_payload(manager)
    await save_container(manager_container)

    async with uow_factory.create(QueryBuilder(mutating=True).build()) as uow:
        resources = uow.get_resources()

        operation_log1 = AutoUnclaimPurchaseOperationLogPayload(
            purchase_id=uuid4(), reason="test"
        )
        log_operation(resources, operation_log1)
        operation_log2 = RefundPurchaseOperationLogPayload(
            purchase_id=uuid4(), amount=Decimal(1)
        )
        log_operation(resources, operation_log2)
        operation_log3 = CancelPurchaseOperationLogPayload(purchase_id=uuid4())
        log_operation(resources, operation_log3)
        uow.mark_commit()

    operation_log_schemas = await operation_log_service.get_after_sequence(
        access_payload, 0, 3
    )
    assert len(operation_log_schemas) == 3

    operation_log_schemas = await operation_log_service.get_after_sequence(
        access_payload, 1, 1
    )
    assert (
        operation_log_schemas[0].operation_code
        == OperationCodeEnum.REFUND_PURCHASE.value
    )

    operation_log_schemas = await operation_log_service.get_before_sequence(
        access_payload, 3, 2
    )
    assert (
        operation_log_schemas[1].operation_code
        == OperationCodeEnum.REFUND_PURCHASE.value
    )
