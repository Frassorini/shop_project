import pytest
from dishka.async_container import AsyncContainer
from pydantic import SecretStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from shop_project.application.schemas.credential_schema import (
    EmailCredentialSchema,
    LoginCredentialSchema,
    PhoneCredentialSchema,
)
from shop_project.application.schemas.totp_request_schema import (
    EmailTotpRequestSchema,
    SmsTotpRequestSchema,
)
from shop_project.application.services.registration_service import RegistrationService
from shop_project.application.services.totp_challenge_service import (
    TotpChallengeService,
)
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.infrastructure.entities.account import Account
from shop_project.infrastructure.notifications.inmemory_email_notification_service import (
    InMemoryEmailNotificationService,
)
from shop_project.infrastructure.notifications.inmemory_sms_notification_service import (
    InMemorySMSNotificationService,
)
from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWorkFactory


@pytest.mark.asyncio
async def test_register_customer_sms_code_flow(
    async_container: AsyncContainer,
    uow_factory: UnitOfWorkFactory,
) -> None:
    register_service = await async_container.get(RegistrationService)
    totp_challenge_service = await async_container.get(TotpChallengeService)
    sms_service = await async_container.get(InMemorySMSNotificationService)

    totp_request = SmsTotpRequestSchema(identifier=PhoneNumber("+7(999)123-45-67"))

    await totp_challenge_service.begin_sms_challenge(totp_request)

    mesg = await sms_service.get_last_message()
    assert mesg
    code = mesg.body.split("Your TOTP code is: ")[1]

    request = PhoneCredentialSchema(
        identifier=totp_request.identifier,
        plaintext_secret=SecretStr(code),
    )

    await register_service.register_customer(request)

    async with uow_factory.create(
        QueryBuilder(mutating=False)
        .load(Account)
        .from_attribute("phone_number", [request.identifier])
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
        customer = resources.get_one_by_attribute(
            Customer, "entity_id", account.entity_id
        )

        assert account.phone_number == request.identifier
        assert customer


@pytest.mark.asyncio
async def test_register_employee_email_code_flow(
    async_container: AsyncContainer,
    uow_factory: UnitOfWorkFactory,
) -> None:
    register_service = await async_container.get(RegistrationService)
    totp_challenge_service = await async_container.get(TotpChallengeService)
    email_service = await async_container.get(InMemoryEmailNotificationService)

    totp_request = EmailTotpRequestSchema(identifier="example@example.com")

    await totp_challenge_service.begin_email_challenge(totp_request)

    mesg = await email_service.get_last_message()
    assert mesg
    code = mesg.body.split("Your TOTP code is: ")[1]

    request = EmailCredentialSchema(
        identifier=totp_request.identifier,
        plaintext_secret=SecretStr(code),
    )

    await register_service.register_employee(request)

    async with uow_factory.create(
        QueryBuilder(mutating=False)
        .load(Account)
        .from_attribute("email", [request.identifier])
        .no_lock()
        .load(Employee)
        .from_previous(0)
        .no_lock()
        .build()
    ) as uow:
        resources = uow.get_resorces()

        account = resources.get_one_by_attribute(Account, "email", request.identifier)

        employee = resources.get_one_by_attribute(
            Employee, "entity_id", account.entity_id
        )

        assert account.email == request.identifier
        assert employee


@pytest.mark.asyncio
async def test_register_manager_password_flow(
    async_container: AsyncContainer,
    uow_factory: UnitOfWorkFactory,
) -> None:
    register_service = await async_container.get(RegistrationService)
    totp_challenge_service = await async_container.get(TotpChallengeService)

    request = LoginCredentialSchema(
        identifier="manager",
        plaintext_secret=SecretStr("password"),
    )

    await register_service.register_manager(request)

    async with uow_factory.create(
        QueryBuilder(mutating=False)
        .load(Account)
        .from_attribute("login", [request.identifier])
        .no_lock()
        .load(Manager)
        .from_previous(0)
        .no_lock()
        .build()
    ) as uow:
        resources = uow.get_resorces()

        account = resources.get_one_by_attribute(Account, "login", request.identifier)
        manager = resources.get_one_by_attribute(
            Manager, "entity_id", account.entity_id
        )

        assert account.login == request.identifier
        assert manager


# @pytest.mark.asyncio
# async def test_register_employee_email_password(
#     async_container: AsyncContainer,
#     uow_factory: UnitOfWorkFactory,
# ) -> None:
#     subject_type = Employee

#     register_service = await async_container.get(RegistrationService)

#     request = EmailRegisterRequestSchema(
#         identifier="example@ya.ru",
#         credential=SecretStr("password"),
#     )

#     await register_service.register_employee(request)

#     async with uow_factory.create(
#         QueryBuilder(mutating=False)
#         .load(Account)
#         .from_attribute("email", [request.identifier])
#         .no_lock()
#         .load(subject_type)
#         .from_previous(0)
#         .no_lock()
#         .build()
#     ) as uow:
#         resources = uow.get_resorces()

#         account = resources.get_one_by_attribute(Account, "email", request.identifier)
#         secret = resources.get_one_by_attribute(Secret, "account_id", account.entity_id)
#         subject = resources.get_one_by_attribute(
#             subject_type, "entity_id", secret.account_id
#         )

#         assert account.email == request.identifier
#         assert secret
#         assert subject


# @pytest.mark.asyncio
# async def test_register_manager_login_password(
#     async_container: AsyncContainer,
#     uow_factory: UnitOfWorkFactory,
# ) -> None:
#     subject_type = Manager

#     register_service = await async_container.get(RegistrationService)

#     request = LoginRegisterRequestSchema(
#         identifier="manager",
#         credential=SecretStr("password"),
#     )

#     await register_service.register_manager(request)

#     async with uow_factory.create(
#         QueryBuilder(mutating=False)
#         .load(Account)
#         .from_attribute("login", [request.identifier])
#         .no_lock()
#         .load(Secret)
#         .from_previous(0)
#         .no_lock()
#         .load(subject_type)
#         .from_previous(0)
#         .no_lock()
#         .build()
#     ) as uow:
#         resources = uow.get_resorces()

#         account = resources.get_all(Account)[0]
#         secret = resources.get_one_by_attribute(Secret, "account_id", account.entity_id)
#         subject = resources.get_one_by_attribute(
#             subject_type, "entity_id", secret.account_id
#         )

#         assert account.login == request.identifier
#         assert secret
#         assert subject
