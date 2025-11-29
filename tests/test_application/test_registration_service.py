import pytest
from dishka.async_container import AsyncContainer
from pydantic import SecretStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from shop_project.application.schemas.register_request_schema import (
    EmailRegisterRequestSchema,
    LoginRegisterRequestSchema,
    PhoneRegisterRequestSchema,
)
from shop_project.application.services.registration_service import RegistrationService
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.infrastructure.entities.account import Account
from shop_project.infrastructure.entities.secret import Secret
from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWorkFactory


@pytest.mark.asyncio
async def test_register_customer_phone_password(
    async_container: AsyncContainer,
    uow_factory: UnitOfWorkFactory,
) -> None:
    register_service = await async_container.get(RegistrationService)

    request = PhoneRegisterRequestSchema(
        identifier=PhoneNumber("+7(999)999-99-99"),
        credential=SecretStr("password"),
    )

    await register_service.register_customer(request)

    async with uow_factory.create(
        QueryBuilder(mutating=False)
        .load(Account)
        .from_attribute("phone_number", [request.identifier])
        .no_lock()
        .load(Secret)
        .from_previous(0)
        .no_lock()
        .load(Customer)
        .from_previous(0)
        .no_lock()
        .build()
    ) as uow:
        resources = uow.get_resorces()

        account = resources.get_one_by_attribute(
            Account, "phone_number", request.identifier
        )
        secret = resources.get_one_by_attribute(Secret, "account_id", account.entity_id)
        customer = resources.get_one_by_attribute(
            Customer, "entity_id", secret.account_id
        )

        assert account.phone_number == request.identifier
        assert secret
        assert customer


@pytest.mark.asyncio
async def test_register_employee_email_password(
    async_container: AsyncContainer,
    uow_factory: UnitOfWorkFactory,
) -> None:
    subject_type = Employee

    register_service = await async_container.get(RegistrationService)

    request = EmailRegisterRequestSchema(
        identifier="example@ya.ru",
        credential=SecretStr("password"),
    )

    await register_service.register_employee(request)

    async with uow_factory.create(
        QueryBuilder(mutating=False)
        .load(Account)
        .from_attribute("email", [request.identifier])
        .no_lock()
        .load(Secret)
        .from_previous(0)
        .no_lock()
        .load(subject_type)
        .from_previous(0)
        .no_lock()
        .build()
    ) as uow:
        resources = uow.get_resorces()

        account = resources.get_one_by_attribute(Account, "email", request.identifier)
        secret = resources.get_one_by_attribute(Secret, "account_id", account.entity_id)
        subject = resources.get_one_by_attribute(
            subject_type, "entity_id", secret.account_id
        )

        assert account.email == request.identifier
        assert secret
        assert subject


@pytest.mark.asyncio
async def test_register_manager_login_password(
    async_container: AsyncContainer,
    uow_factory: UnitOfWorkFactory,
) -> None:
    subject_type = Manager

    register_service = await async_container.get(RegistrationService)

    request = LoginRegisterRequestSchema(
        identifier="manager",
        credential=SecretStr("password"),
    )

    await register_service.register_manager(request)

    async with uow_factory.create(
        QueryBuilder(mutating=False)
        .load(Account)
        .from_attribute("login", [request.identifier])
        .no_lock()
        .load(Secret)
        .from_previous(0)
        .no_lock()
        .load(subject_type)
        .from_previous(0)
        .no_lock()
        .build()
    ) as uow:
        resources = uow.get_resorces()

        account = resources.get_all(Account)[0]
        secret = resources.get_one_by_attribute(Secret, "account_id", account.entity_id)
        subject = resources.get_one_by_attribute(
            subject_type, "entity_id", secret.account_id
        )

        assert account.login == request.identifier
        assert secret
        assert subject
