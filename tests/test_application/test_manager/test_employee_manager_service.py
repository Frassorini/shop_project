from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Sequence,
    Type,
)

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.entities.operation_log.operation_code import (
    OperationCodeEnum,
)
from shop_project.application.entities.operation_log.operation_log import OperationLog
from shop_project.application.manager.commands.employee_manager_service import (
    EmployeeManagerService,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.subject import Subject
from tests.helpers import AggregateContainer


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_employee_manager_service_authorize(
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    async_container: AsyncContainer,
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    manager_container_factory: Callable[[], AggregateContainer],
    employee_container_factory: Callable[[], AggregateContainer],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
    ensure_operation_log_amount: Callable[[int], Awaitable[Sequence[OperationLog]]],
) -> None:
    manager_container = manager_container_factory()
    manager: Manager = (
        manager_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_payload = await get_subject_access_token_payload(manager)
    employee_container: AggregateContainer = employee_container_factory()
    employee: Employee = (
        employee_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    employee_manager_service = await async_container.get(EmployeeManagerService)
    manager_container.merge(employee_container)
    await save_container(manager_container)

    employee_schema = await employee_manager_service.authorize_employee(
        access_payload=access_payload, employee_id=employee.entity_id
    )

    employee_new: Employee = await uow_get_one_single_model(
        Employee, "entity_id", employee.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert employee_new.name == employee_schema.name
    assert employee_new.entity_id == employee.entity_id
    assert employee_new.is_authorized()

    logs = await ensure_operation_log_amount(1)
    codes = [log.operation_code for log in logs]
    assert OperationCodeEnum.AUTHORIZE_EMPLOYEE.value in codes


@pytest.mark.asyncio
@pytest.mark.inmemory
async def test_employee_manager_service_unauthorize(
    uow_get_one_single_model: Callable[
        [Type[PersistableEntity], str, Any], Awaitable[PersistableEntity]
    ],
    async_container: AsyncContainer,
    save_container: Callable[[AggregateContainer], Coroutine[None, None, None]],
    manager_container_factory: Callable[[], AggregateContainer],
    employee_container_factory: Callable[[], AggregateContainer],
    get_subject_access_token_payload: Callable[
        [Subject], Awaitable[AccessTokenPayload]
    ],
    ensure_operation_log_amount: Callable[[int], Awaitable[Sequence[OperationLog]]],
) -> None:
    manager_container = manager_container_factory()
    manager: Manager = (
        manager_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    access_payload = await get_subject_access_token_payload(manager)
    employee_container: AggregateContainer = employee_container_factory()
    employee: Employee = (
        employee_container.aggregate
    )  # pyright: ignore[reportAssignmentType]
    employee.authorize()
    employee_manager_service = await async_container.get(EmployeeManagerService)
    manager_container.merge(employee_container)
    await save_container(manager_container)

    employee_schema = await employee_manager_service.unauthorize_employee(
        access_payload=access_payload, employee_id=employee.entity_id
    )

    employee_new: Employee = await uow_get_one_single_model(
        Employee, "entity_id", employee.entity_id
    )  # pyright: ignore[reportAssignmentType]
    assert employee_new.name == employee_schema.name
    assert employee_new.entity_id == employee.entity_id
    assert not employee_new.is_authorized()

    logs = await ensure_operation_log_amount(1)
    codes = [log.operation_code for log in logs]
    assert OperationCodeEnum.UNAUTHORIZE_EMPLOYEE.value in codes
