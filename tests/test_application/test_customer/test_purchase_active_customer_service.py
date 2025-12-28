from datetime import datetime, timedelta, timezone
from typing import (
    Any,
    Awaitable,
    Callable,
    Sequence,
    Type,
)

import pytest
from dishka.async_container import AsyncContainer
from freezegun import freeze_time

from shop_project.application.background.base_task_handler import NullTaskParams
from shop_project.application.background.implementations.purchase_flow_handler import (
    BatchFinalizeNotPaidTasksHandler,
    BatchPaidReservationTimeOutTaskHandler,
    BatchWaitPaymentTaskHandler,
    BatchWaitRefundTaskHandler,
)
from shop_project.application.customer.commands.purchase_active_customer_service import (
    PurchaseActiveCustomerService,
)
from shop_project.application.customer.schemas.purchase_active_schema import (
    PurchaseActivationSchema,
    PurchaseActiveSchema,
)
from shop_project.application.entities.operation_log.operation_code import (
    OperationCodeEnum,
)
from shop_project.application.entities.operation_log.operation_log import OperationLog
from shop_project.application.entities.task import Task, create_task
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.interfaces.interface_task_sender import ITaskSender
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.escrow_account import (
    EscrowAccount,
    EscrowAccountState,
)
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_summary import (
    PurchaseSummary,
    PurchaseSummaryReason,
)
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.subject import Subject
from shop_project.infrastructure.payments.inmemory_payment_gateway import (
    InMemoryPaymentGateway,
)
from tests.helpers import AggregateContainer


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_activate_purchase(
    purchase_activation: Callable[
        [AggregateContainer], Awaitable[PurchaseActivationSchema]
    ],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    customer_container_factory: Callable[[], AggregateContainer],
    ensure_operation_log_amount: Callable[[int], Awaitable[Sequence[OperationLog]]],
) -> None:
    customer_container: AggregateContainer = customer_container_factory()
    customer: Customer = (
        customer_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    purchase_activation: PurchaseActivationSchema = await purchase_activation(
        customer_container
    )
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active

    escrow_account: EscrowAccount = await uow_get_one_single_model(
        EscrowAccount, "entity_id", purchase_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    purchase_active: PurchaseActive = await uow_get_one_single_model(
        PurchaseActive, "entity_id", purchase_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert purchase_schema.payment_state == EscrowAccountState.PENDING.value
    assert purchase_schema.entity_id == purchase_active.entity_id
    assert purchase_schema.price == escrow_account.total_amount

    logs = await ensure_operation_log_amount(1)
    codes = [log.operation_code for log in logs]
    assert OperationCodeEnum.ACTIVATE_PURCHASE.value in codes


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_cancel_payment(
    async_container: AsyncContainer,
    purchase_activation: Callable[
        [AggregateContainer], Awaitable[PurchaseActivationSchema]
    ],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    inmem_save_and_send_task: Callable[[Task], Awaitable[None]],
    customer_container_factory: Callable[[], AggregateContainer],
    ensure_operation_log_amount: Callable[[int], Awaitable[Sequence[OperationLog]]],
) -> None:
    customer_container: AggregateContainer = customer_container_factory()
    customer: Customer = (
        customer_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    task_sender = await async_container.get(ITaskSender)
    payment_gateway = await async_container.get(InMemoryPaymentGateway)
    purchase_activation: PurchaseActivationSchema = await purchase_activation(
        customer_container
    )
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active

    payment_gateway.cancel_pending()

    await inmem_save_and_send_task(
        create_task(BatchWaitPaymentTaskHandler, NullTaskParams())
    )

    escrow_account: EscrowAccount = await uow_get_one_single_model(
        EscrowAccount, "entity_id", purchase_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    purchase_active: PurchaseActive = await uow_get_one_single_model(
        PurchaseActive, "entity_id", purchase_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert escrow_account.state == EscrowAccountState.PAYMENT_CANCELLED
    assert purchase_schema.entity_id == purchase_active.entity_id
    assert purchase_schema.price == escrow_account.total_amount

    logs = await ensure_operation_log_amount(1)
    codes = [log.operation_code for log in logs]
    assert OperationCodeEnum.ACTIVATE_PURCHASE.value in codes


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_finalize_cancelled(
    async_container: AsyncContainer,
    purchase_activation: Callable[
        [AggregateContainer], Awaitable[PurchaseActivationSchema]
    ],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    uow_get_all_single_model: Callable[
        [Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]
    ],
    inmem_save_and_send_task: Callable[[Task], Awaitable[None]],
    customer_container_factory: Callable[[], AggregateContainer],
    ensure_operation_log_amount: Callable[[int], Awaitable[Sequence[OperationLog]]],
) -> None:
    customer_container: AggregateContainer = customer_container_factory()
    customer: Customer = (
        customer_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    task_sender = await async_container.get(ITaskSender)

    payment_gateway = await async_container.get(InMemoryPaymentGateway)
    purchase_activation: PurchaseActivationSchema = await purchase_activation(
        customer_container
    )
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active
    payment_gateway.cancel_pending()
    await inmem_save_and_send_task(
        create_task(BatchWaitPaymentTaskHandler, NullTaskParams())
    )

    await inmem_save_and_send_task(
        create_task(BatchFinalizeNotPaidTasksHandler, NullTaskParams())
    )

    assert not await uow_get_all_single_model(PurchaseActive)
    summary: PurchaseSummary = (await uow_get_all_single_model(PurchaseSummary))[
        0
    ]  # pyright: ignore[reportAssignmentType]
    escrow_account: EscrowAccount = await uow_get_one_single_model(
        EscrowAccount, "entity_id", purchase_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert summary.reason == PurchaseSummaryReason.PAYMENT_CANCELLED
    assert escrow_account.state == EscrowAccountState.FINALIZED

    logs = await ensure_operation_log_amount(2)
    codes = [log.operation_code for log in logs]
    assert OperationCodeEnum.ACTIVATE_PURCHASE.value in codes
    assert OperationCodeEnum.CANCEL_PURCHASE.value in codes


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_confirm_payment(
    async_container: AsyncContainer,
    purchase_activation: Callable[
        [AggregateContainer], Awaitable[PurchaseActivationSchema]
    ],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    inmem_save_and_send_task: Callable[[Task], Awaitable[None]],
    customer_container_factory: Callable[[], AggregateContainer],
    ensure_operation_log_amount: Callable[[int], Awaitable[Sequence[OperationLog]]],
) -> None:
    customer_container: AggregateContainer = customer_container_factory()
    customer: Customer = (
        customer_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    task_sender = await async_container.get(ITaskSender)

    payment_gateway = await async_container.get(InMemoryPaymentGateway)
    purchase_activation: PurchaseActivationSchema = await purchase_activation(
        customer_container
    )
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active

    payment_gateway.pay_pending()
    await inmem_save_and_send_task(
        create_task(BatchWaitPaymentTaskHandler, NullTaskParams())
    )

    escrow_account: EscrowAccount = await uow_get_one_single_model(
        EscrowAccount, "entity_id", purchase_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    purchase_active: PurchaseActive = await uow_get_one_single_model(
        PurchaseActive, "entity_id", purchase_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert escrow_account.state == EscrowAccountState.PAID
    assert purchase_schema.entity_id == purchase_active.entity_id
    assert purchase_schema.price == escrow_account.total_amount

    logs = await ensure_operation_log_amount(2)
    codes = [log.operation_code for log in logs]
    assert OperationCodeEnum.ACTIVATE_PURCHASE.value in codes
    assert OperationCodeEnum.PAY_PURCHASE.value in codes


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_manual_unclaim(
    async_container: AsyncContainer,
    purchase_activation: Callable[
        [AggregateContainer], Awaitable[PurchaseActivationSchema]
    ],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    uow_get_all_single_model: Callable[
        [Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]
    ],
    inmem_save_and_send_task: Callable[[Task], Awaitable[None]],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
    customer_container_factory: Callable[[], AggregateContainer],
    ensure_operation_log_amount: Callable[[int], Awaitable[Sequence[OperationLog]]],
) -> None:
    customer_container: AggregateContainer = customer_container_factory()
    customer: Customer = (
        customer_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_token = await get_subject_access_token_payload(customer)
    task_sender = await async_container.get(ITaskSender)
    payment_gateway = await async_container.get(InMemoryPaymentGateway)
    purchase_activation: PurchaseActivationSchema = await purchase_activation(
        customer_container
    )
    purchase_service = await async_container.get(PurchaseActiveCustomerService)
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active
    payment_gateway.pay_pending()
    await inmem_save_and_send_task(
        create_task(BatchWaitPaymentTaskHandler, NullTaskParams())
    )

    await purchase_service.unclaim(access_token, purchase_schema.entity_id)

    assert not await uow_get_all_single_model(PurchaseActive)
    summary: PurchaseSummary = (await uow_get_all_single_model(PurchaseSummary))[
        0
    ]  # pyright: ignore[reportAssignmentType]
    escrow_account: EscrowAccount = await uow_get_one_single_model(
        EscrowAccount, "entity_id", purchase_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert summary.reason == PurchaseSummaryReason.NOT_CLAIMED
    assert escrow_account.state == EscrowAccountState.REFUNDING

    logs = await ensure_operation_log_amount(3)
    codes = [log.operation_code for log in logs]
    assert OperationCodeEnum.ACTIVATE_PURCHASE.value in codes
    assert OperationCodeEnum.PAY_PURCHASE.value in codes
    assert OperationCodeEnum.MANUAL_UNCLAIM_PURCHASE.value in codes


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_auto_unclaim(
    async_container: AsyncContainer,
    purchase_activation: Callable[
        [AggregateContainer], Awaitable[PurchaseActivationSchema]
    ],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    uow_get_all_single_model: Callable[
        [Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]
    ],
    inmem_save_and_send_task: Callable[[Task], Awaitable[None]],
    customer_container_factory: Callable[[], AggregateContainer],
    ensure_operation_log_amount: Callable[[int], Awaitable[Sequence[OperationLog]]],
) -> None:
    customer_container: AggregateContainer = customer_container_factory()
    customer: Customer = (
        customer_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    task_sender = await async_container.get(ITaskSender)

    payment_gateway = await async_container.get(InMemoryPaymentGateway)
    purchase_activation: PurchaseActivationSchema = await purchase_activation(
        customer_container
    )
    purchase_service = await async_container.get(PurchaseActiveCustomerService)
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active
    payment_gateway.pay_pending()
    await inmem_save_and_send_task(
        create_task(BatchWaitPaymentTaskHandler, NullTaskParams())
    )

    with freeze_time(datetime.now(tz=timezone.utc) + timedelta(weeks=10)):
        await inmem_save_and_send_task(
            create_task(BatchPaidReservationTimeOutTaskHandler, NullTaskParams())
        )

    assert not await uow_get_all_single_model(PurchaseActive)
    summary: PurchaseSummary = (await uow_get_all_single_model(PurchaseSummary))[
        0
    ]  # pyright: ignore[reportAssignmentType]
    escrow_account: EscrowAccount = await uow_get_one_single_model(
        EscrowAccount, "entity_id", purchase_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert summary.reason == PurchaseSummaryReason.NOT_CLAIMED
    assert escrow_account.state == EscrowAccountState.REFUNDING

    logs = await ensure_operation_log_amount(3)
    codes = [log.operation_code for log in logs]
    assert OperationCodeEnum.ACTIVATE_PURCHASE.value in codes
    assert OperationCodeEnum.PAY_PURCHASE.value in codes
    assert OperationCodeEnum.AUTO_UNCLAIM_PURCHASE.value in codes


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_confirm_refund(
    async_container: AsyncContainer,
    purchase_activation: Callable[
        [AggregateContainer], Awaitable[PurchaseActivationSchema]
    ],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    uow_get_all_single_model: Callable[
        [Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]
    ],
    inmem_save_and_send_task: Callable[[Task], Awaitable[None]],
    customer_container_factory: Callable[[], AggregateContainer],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
    ensure_operation_log_amount: Callable[[int], Awaitable[Sequence[OperationLog]]],
) -> None:
    customer_container: AggregateContainer = customer_container_factory()
    customer: Customer = (
        customer_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_token = await get_subject_access_token_payload(customer)
    task_sender = await async_container.get(ITaskSender)
    payment_gateway = await async_container.get(InMemoryPaymentGateway)
    purchase_activation: PurchaseActivationSchema = await purchase_activation(
        customer_container
    )
    purchase_service = await async_container.get(PurchaseActiveCustomerService)
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active
    payment_gateway.pay_pending()
    await inmem_save_and_send_task(
        create_task(BatchWaitPaymentTaskHandler, NullTaskParams())
    )
    await purchase_service.unclaim(access_token, purchase_schema.entity_id)
    payment_gateway.complete_refunding()

    await inmem_save_and_send_task(
        create_task(BatchWaitRefundTaskHandler, NullTaskParams())
    )

    assert not await uow_get_all_single_model(PurchaseActive)
    summary: PurchaseSummary = (await uow_get_all_single_model(PurchaseSummary))[
        0
    ]  # pyright: ignore[reportAssignmentType]
    escrow_account: EscrowAccount = await uow_get_one_single_model(
        EscrowAccount, "entity_id", purchase_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert summary.reason == PurchaseSummaryReason.NOT_CLAIMED
    assert escrow_account.state == EscrowAccountState.FINALIZED

    logs = await ensure_operation_log_amount(4)
    codes = [log.operation_code for log in logs]
    assert OperationCodeEnum.ACTIVATE_PURCHASE.value in codes
    assert OperationCodeEnum.PAY_PURCHASE.value in codes
    assert OperationCodeEnum.MANUAL_UNCLAIM_PURCHASE.value in codes
    assert OperationCodeEnum.REFUND_PURCHASE.value in codes
