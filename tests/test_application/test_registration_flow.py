from typing import Awaitable, Callable
from uuid import UUID

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.schemas.session_refresh_schema import SessionRefreshSchema
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.infrastructure.entities.account import Account
from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWorkFactory
from shop_project.shared.phone_str import validate_phone_number


@pytest.mark.asyncio
async def test_register_customer_sms_code_flow(
    async_container: AsyncContainer,
    uow_factory: UnitOfWorkFactory,
    register_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    get_account_id_by_access_token: Callable[[str], UUID],
) -> None:
    phone_number = validate_phone_number("+79991234567")

    refresh = await register_subject(Customer, phone_number=phone_number)
    account_id = get_account_id_by_access_token(refresh.access_token.get_secret_value())

    async with uow_factory.create(
        QueryBuilder(mutating=False)
        .load(Account)
        .from_attribute("phone_number", [phone_number])
        .no_lock()
        .load(Customer)
        .from_previous(0)
        .no_lock()
        .build()
    ) as uow:
        resources = uow.get_resorces()

        account = resources.get_one_by_attribute(Account, "phone_number", phone_number)
        customer = resources.get_one_by_attribute(
            Customer, "entity_id", account.entity_id
        )

        assert account.phone_number == phone_number
        assert customer


@pytest.mark.asyncio
async def test_register_employee_email_code_flow(
    async_container: AsyncContainer,
    uow_factory: UnitOfWorkFactory,
    register_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    get_account_id_by_access_token: Callable[[str], UUID],
) -> None:
    email = "example@example.com"

    refresh = await register_subject(Employee, email=email)
    account_id = get_account_id_by_access_token(refresh.access_token.get_secret_value())

    async with uow_factory.create(
        QueryBuilder(mutating=False)
        .load(Account)
        .from_attribute("email", [email])
        .no_lock()
        .load(Employee)
        .from_previous(0)
        .no_lock()
        .build()
    ) as uow:
        resources = uow.get_resorces()

        account = resources.get_one_by_attribute(Account, "email", email)

        employee = resources.get_one_by_attribute(
            Employee, "entity_id", account.entity_id
        )

        assert account.email == email
        assert employee


@pytest.mark.asyncio
async def test_register_manager_login_flow(
    async_container: AsyncContainer,
    uow_factory: UnitOfWorkFactory,
    register_subject: Callable[..., Awaitable[SessionRefreshSchema]],
    get_account_id_by_access_token: Callable[[str], UUID],
) -> None:
    login = "manager"
    password = "password"

    refresh = await register_subject(Manager, login=login, password=password)
    account_id = get_account_id_by_access_token(refresh.access_token.get_secret_value())

    async with uow_factory.create(
        QueryBuilder(mutating=False)
        .load(Account)
        .from_attribute("login", [login])
        .no_lock()
        .load(Manager)
        .from_previous(0)
        .no_lock()
        .build()
    ) as uow:
        resources = uow.get_resorces()

        account = resources.get_one_by_attribute(Account, "login", login)
        manager = resources.get_one_by_attribute(
            Manager, "entity_id", account.entity_id
        )

        assert account.login == login
        assert manager
