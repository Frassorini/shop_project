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

from shop_project.application.interfaces.interface_task_factory import ITaskFactory
from shop_project.application.interfaces.interface_task_sender import ITaskSender
from shop_project.application.schemas.purchase_active_schema import (
    PurchaseActivationSchema,
    PurchaseActiveSchema,
)
from shop_project.application.schemas.purchase_summary_schema import (
    PurchaseSummarySchema,
)
from shop_project.application.services.authentication_service import (
    AuthenticationService,
)
from shop_project.application.services.purchase_service import PurchaseService
from shop_project.application.tasks.base_task_handler import NullTaskParams
from shop_project.application.tasks.implementations.purchase_flow_handler import (
    BatchFinalizeNotPaidTasksHandler,
    BatchPaidReservationTimeOutTaskHandler,
    BatchWaitPaymentTaskHandler,
    BatchWaitRefundTaskHandler,
)
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
from shop_project.infrastructure.payments.inmemory_payment_gateway import (
    InMemoryPaymentGateway,
)


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_activate_purchase(
    purchase_activation: Callable[[], Awaitable[PurchaseActivationSchema]],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
) -> None:
    purchase_activation: PurchaseActivationSchema = await purchase_activation()
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


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_cancel_payment(
    async_container: AsyncContainer,
    purchase_activation: Callable[[], Awaitable[PurchaseActivationSchema]],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
) -> None:
    task_sender = await async_container.get(ITaskSender)
    task_factory = await async_container.get(ITaskFactory)
    payment_gateway = await async_container.get(InMemoryPaymentGateway)
    purchase_activation: PurchaseActivationSchema = await purchase_activation()
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active

    payment_gateway.cancel_pending()
    await task_sender.send(
        task_factory.create(BatchWaitPaymentTaskHandler, NullTaskParams())
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


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_finalize_cancelled(
    async_container: AsyncContainer,
    purchase_activation: Callable[[], Awaitable[PurchaseActivationSchema]],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    uow_get_all_single_model: Callable[
        [Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]
    ],
) -> None:
    task_sender = await async_container.get(ITaskSender)
    task_factory = await async_container.get(ITaskFactory)
    payment_gateway = await async_container.get(InMemoryPaymentGateway)
    purchase_activation: PurchaseActivationSchema = await purchase_activation()
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active
    payment_gateway.cancel_pending()
    await task_sender.send(
        task_factory.create(BatchWaitPaymentTaskHandler, NullTaskParams())
    )

    await task_sender.send(
        task_factory.create(BatchFinalizeNotPaidTasksHandler, NullTaskParams())
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


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_confirm_payment(
    async_container: AsyncContainer,
    purchase_activation: Callable[[], Awaitable[PurchaseActivationSchema]],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
) -> None:
    task_sender = await async_container.get(ITaskSender)
    task_factory = await async_container.get(ITaskFactory)
    payment_gateway = await async_container.get(InMemoryPaymentGateway)
    purchase_activation: PurchaseActivationSchema = await purchase_activation()
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active

    payment_gateway.pay_pending()
    await task_sender.send(
        task_factory.create(BatchWaitPaymentTaskHandler, NullTaskParams())
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


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_manual_unclaim(
    async_container: AsyncContainer,
    purchase_activation: Callable[[], Awaitable[PurchaseActivationSchema]],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    uow_get_all_single_model: Callable[
        [Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]
    ],
) -> None:
    task_sender = await async_container.get(ITaskSender)
    task_factory = await async_container.get(ITaskFactory)
    payment_gateway = await async_container.get(InMemoryPaymentGateway)
    purchase_activation: PurchaseActivationSchema = await purchase_activation()
    purchase_service = await async_container.get(PurchaseService)
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active
    payment_gateway.pay_pending()
    await task_sender.send(
        task_factory.create(BatchWaitPaymentTaskHandler, NullTaskParams())
    )

    await purchase_service.unclaim(
        purchase_schema.customer_id, purchase_schema.entity_id
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


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_auto_unclaim(
    async_container: AsyncContainer,
    purchase_activation: Callable[[], Awaitable[PurchaseActivationSchema]],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    uow_get_all_single_model: Callable[
        [Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]
    ],
) -> None:
    task_sender = await async_container.get(ITaskSender)
    task_factory = await async_container.get(ITaskFactory)
    payment_gateway = await async_container.get(InMemoryPaymentGateway)
    purchase_activation: PurchaseActivationSchema = await purchase_activation()
    purchase_service = await async_container.get(PurchaseService)
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active
    payment_gateway.pay_pending()
    await task_sender.send(
        task_factory.create(BatchWaitPaymentTaskHandler, NullTaskParams())
    )

    with freeze_time(datetime.now(tz=timezone.utc) + timedelta(weeks=10)):
        await task_sender.send(
            task_factory.create(
                BatchPaidReservationTimeOutTaskHandler, NullTaskParams()
            )
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


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_confirm_refund(
    async_container: AsyncContainer,
    purchase_activation: Callable[[], Awaitable[PurchaseActivationSchema]],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    uow_get_all_single_model: Callable[
        [Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]
    ],
) -> None:
    task_sender = await async_container.get(ITaskSender)
    task_factory = await async_container.get(ITaskFactory)
    payment_gateway = await async_container.get(InMemoryPaymentGateway)
    purchase_activation: PurchaseActivationSchema = await purchase_activation()
    purchase_service = await async_container.get(PurchaseService)
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active
    payment_gateway.pay_pending()
    await task_sender.send(
        task_factory.create(BatchWaitPaymentTaskHandler, NullTaskParams())
    )
    await purchase_service.unclaim(
        purchase_schema.customer_id, purchase_schema.entity_id
    )
    payment_gateway.complete_refunding()

    await task_sender.send(
        task_factory.create(BatchWaitRefundTaskHandler, NullTaskParams())
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


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_purchase_flow_claim(
    async_container: AsyncContainer,
    purchase_activation: Callable[[], Awaitable[PurchaseActivationSchema]],
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    uow_get_all_single_model: Callable[
        [Type[PersistableEntity]], Awaitable[Sequence[PersistableEntity]]
    ],
) -> None:
    task_sender = await async_container.get(ITaskSender)
    task_factory = await async_container.get(ITaskFactory)
    payment_gateway = await async_container.get(InMemoryPaymentGateway)
    auhentication_service = await async_container.get(AuthenticationService)
    purchase_activation: PurchaseActivationSchema = await purchase_activation()
    purchase_service = await async_container.get(PurchaseService)
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active
    payment_gateway.pay_pending()
    await task_sender.send(
        task_factory.create(BatchWaitPaymentTaskHandler, NullTaskParams())
    )

    claim_token = await auhentication_service.get_claim_token(
        purchase_schema.customer_id
    )
    summaries: list[PurchaseSummarySchema] = await purchase_service.claim(
        claim_token.claim_token
    )

    assert len(summaries) == 1
    assert summaries[0].reason == PurchaseSummaryReason.CLAIMED.value
    assert not await uow_get_all_single_model(PurchaseActive)
    summary: PurchaseSummary = (await uow_get_all_single_model(PurchaseSummary))[
        0
    ]  # pyright: ignore[reportAssignmentType]
    escrow_account: EscrowAccount = await uow_get_one_single_model(
        EscrowAccount, "entity_id", purchase_schema.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert summary.reason == PurchaseSummaryReason.CLAIMED
    assert escrow_account.state == EscrowAccountState.FINALIZED
