from typing import (
    Any,
    Awaitable,
    Callable,
    Sequence,
    Type,
)

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.background.base_task_handler import NullTaskParams
from shop_project.application.background.implementations.purchase_flow_handler import (
    BatchWaitPaymentTaskHandler,
)
from shop_project.application.customer.commands.purchase_active_customer_service import (
    PurchaseActiveCustomerService,
)
from shop_project.application.customer.schemas.purchase_active_schema import (
    PurchaseActivationSchema,
    PurchaseActiveSchema,
)
from shop_project.application.customer.schemas.purchase_summary_schema import (
    PurchaseSummarySchema,
)
from shop_project.application.employee.commands.purchase_active_employee_service import (
    PurchaseActiveEmployeeService,
)
from shop_project.application.entities.operation_log.operation_code import (
    OperationCodeEnum,
)
from shop_project.application.entities.operation_log.operation_log import OperationLog
from shop_project.application.entities.task import Task, create_task
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.interfaces.interface_task_sender import ITaskSender
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
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
async def test_purchase_flow_claim(
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
    employee_container_factory: Callable[[], AggregateContainer],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
    ensure_operation_log_amount: Callable[[int], Awaitable[Sequence[OperationLog]]],
) -> None:
    employee_container: AggregateContainer = employee_container_factory()
    employee: Employee = (
        employee_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    employee.authorize()
    customer_container: AggregateContainer = customer_container_factory().merge(
        employee_container
    )
    customer: Customer = (
        customer_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    customer_access_token = await get_subject_access_token_payload(customer)
    employee_access_token = await get_subject_access_token_payload(employee)
    task_sender = await async_container.get(ITaskSender)
    payment_gateway = await async_container.get(InMemoryPaymentGateway)
    purchase_activation: PurchaseActivationSchema = await purchase_activation(
        customer_container
    )
    purchase_service = await async_container.get(PurchaseActiveCustomerService)
    purchase_employee_service = await async_container.get(PurchaseActiveEmployeeService)
    purchase_schema: PurchaseActiveSchema = purchase_activation.purchase_active
    payment_gateway.pay_pending()
    await inmem_save_and_send_task(
        create_task(BatchWaitPaymentTaskHandler, NullTaskParams())
    )

    claim_token = await purchase_service.get_claim_token(customer_access_token)
    summaries: list[PurchaseSummarySchema] = await purchase_employee_service.claim(
        employee_access_token, claim_token
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

    logs = await ensure_operation_log_amount(3)
    codes = [log.operation_code for log in logs]
    assert OperationCodeEnum.ACTIVATE_PURCHASE.value in codes
    assert OperationCodeEnum.PAY_PURCHASE.value in codes
    assert OperationCodeEnum.CLAIM_PURCHASE.value in codes
