from datetime import timedelta
from typing import AsyncContextManager, Awaitable, Callable, Coroutine, Type

import pytest
from dishka.container import Container

from shop_project.application.entities.account import Account, SubjectEnum
from shop_project.application.entities.auth_session import AuthSession
from shop_project.application.entities.claim_token import ClaimToken
from shop_project.application.entities.external_id_totp import ExternalIdTotp
from shop_project.application.entities.operation_log.operation_log import OperationLog
from shop_project.application.entities.task import Task
from shop_project.application.shared.dto.mapper import to_dto
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    LockTimeoutException,
)
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.manager import Manager
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.entities.purchase_summary import (
    PurchaseSummary,
    PurchaseSummaryReason,
)
from shop_project.domain.entities.shipment import Shipment
from shop_project.domain.entities.shipment_summary import ShipmentSummary
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.services.shipment_cancel_service import ShipmentCancelService
from shop_project.infrastructure.exceptions import ResourcesException
from shop_project.infrastructure.persistence.query.query_builder import QueryBuilder
from shop_project.infrastructure.persistence.unit_of_work import (
    UnitOfWork,
    UnitOfWorkFactory,
)
from tests.helpers import AggregateContainer


@pytest.mark.asyncio
async def test_operation_log(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
) -> None:
    model_type: Type[PersistableEntity] = OperationLog
    domain_container: AggregateContainer = await prepare_container(model_type)
    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )

        domain_obj.payload_json = "1"

        snapshot_before = to_dto(domain_obj)

        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )

        assert snapshot_before == snapshot_after

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj_from_db: PersistableEntity = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )
        resources.delete(model_type, domain_obj_from_db)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        with pytest.raises(ResourcesException):
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)


@pytest.mark.asyncio
async def test_claim_token(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
) -> None:
    model_type: Type[PersistableEntity] = ClaimToken
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )

        domain_obj.expiration = domain_obj.expiration + timedelta(days=1)

        snapshot_before = to_dto(domain_obj)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )
        assert snapshot_before == snapshot_after

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj_from_db: PersistableEntity = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )
        resources.delete(model_type, domain_obj_from_db)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        with pytest.raises(ResourcesException):
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)


@pytest.mark.asyncio
async def test_account(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
) -> None:
    model_type: Type[PersistableEntity] = Task
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj: Task = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )

        domain_obj.handler = "new handler"

        snapshot_before = to_dto(domain_obj)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )
        assert snapshot_before == snapshot_after

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj_from_db: PersistableEntity = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )
        resources.delete(model_type, domain_obj_from_db)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        with pytest.raises(ResourcesException):
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)


@pytest.mark.asyncio
async def test_external_id_totp(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
) -> None:
    model_type: Type[PersistableEntity] = ExternalIdTotp
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj: ExternalIdTotp = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )

        domain_obj.expiration = domain_obj.expiration + timedelta(days=1)

        snapshot_before = to_dto(domain_obj)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )
        assert snapshot_before == snapshot_after

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj_from_db: PersistableEntity = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )
        resources.delete(model_type, domain_obj_from_db)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        with pytest.raises(ResourcesException):
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)


@pytest.mark.asyncio
async def test_auth_session(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
) -> None:
    model_type: Type[PersistableEntity] = AuthSession
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )

        domain_obj.expiration = domain_obj.expiration + timedelta(days=1)

        snapshot_before = to_dto(domain_obj)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )
        assert snapshot_before == snapshot_after

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj_from_db: PersistableEntity = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )
        resources.delete(model_type, domain_obj_from_db)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        with pytest.raises(ResourcesException):
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)


@pytest.mark.asyncio
async def test_account(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
) -> None:
    model_type: Type[PersistableEntity] = Account
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj: Account = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )

        domain_obj.subject_type = SubjectEnum.EMPLOYEE

        snapshot_before = to_dto(domain_obj)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )
        assert snapshot_before == snapshot_after

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj_from_db: PersistableEntity = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )
        resources.delete(model_type, domain_obj_from_db)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        with pytest.raises(ResourcesException):
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)


@pytest.mark.asyncio
async def test_manager(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
) -> None:
    model_type: Type[PersistableEntity] = Manager
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj: Manager = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )

        domain_obj.name = "new name"

        snapshot_before = to_dto(domain_obj)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )
        assert snapshot_before == snapshot_after

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj_from_db: PersistableEntity = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )
        resources.delete(model_type, domain_obj_from_db)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        with pytest.raises(ResourcesException):
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)


@pytest.mark.asyncio
async def test_employee(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
) -> None:
    model_type: Type[PersistableEntity] = Employee
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj: Employee = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )

        domain_obj.name = "new name"

        snapshot_before = to_dto(domain_obj)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )
        assert snapshot_before == snapshot_after

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj_from_db: PersistableEntity = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )
        resources.delete(model_type, domain_obj_from_db)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        with pytest.raises(ResourcesException):
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)


@pytest.mark.asyncio
async def test_customer(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
) -> None:
    model_type: Type[PersistableEntity] = Customer
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj: Customer = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )

        domain_obj.name = "new name"

        snapshot_before = to_dto(domain_obj)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )
        assert snapshot_before == snapshot_after

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj_from_db: PersistableEntity = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )
        resources.delete(model_type, domain_obj_from_db)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        with pytest.raises(ResourcesException):
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)


@pytest.mark.asyncio
async def test_escrow(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
) -> None:
    model_type: Type[PersistableEntity] = EscrowAccount
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj: EscrowAccount = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )

        domain_obj.mark_as_paid()

        snapshot_before = to_dto(domain_obj)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )
        assert snapshot_before == snapshot_after

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj_from_db: PersistableEntity = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )
        resources.delete(model_type, domain_obj_from_db)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        with pytest.raises(ResourcesException):
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)


@pytest.mark.asyncio
async def test_purchase_draft(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
    uow_delete_and_check: Callable[
        [Type[PersistableEntity], PersistableEntity], Awaitable[None]
    ],
    product_container_factory: Callable[..., AggregateContainer],
) -> None:

    model_type: Type[PersistableEntity] = PurchaseDraft
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .load(Product)
        .from_previous()
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj: PurchaseDraft = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )
        product = product_container_factory(name="test item", amount=10, price=1)
        product_other = product_container_factory(name="test item2", amount=20, price=2)
        resources.put(Product, product.aggregate)
        resources.put(Product, product_other.aggregate)
        domain_obj.add_item(product.aggregate.entity_id, 1)
        domain_obj.add_item(product_other.aggregate.entity_id, 2)

        snapshot_before = to_dto(domain_obj)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )
        assert snapshot_before == snapshot_after

    await uow_delete_and_check(model_type, domain_container.aggregate)


@pytest.mark.asyncio
async def test_purchase_active(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
    uow_delete_and_check: Callable[
        [Type[PersistableEntity], PersistableEntity], Awaitable[None]
    ],
) -> None:

    model_type: Type[PersistableEntity] = PurchaseActive
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .load(Product)
        .from_previous()
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj: PurchaseActive = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )
        domain_obj.finalize()

        snapshot_before = to_dto(domain_obj)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )
        assert snapshot_before == snapshot_after

    await uow_delete_and_check(model_type, domain_container.aggregate)


@pytest.mark.asyncio
async def test_purchase_summary(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
    uow_delete_and_check: Callable[
        [Type[PersistableEntity], PersistableEntity], Awaitable[None]
    ],
) -> None:

    model_type: Type[PersistableEntity] = PurchaseSummary
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .load(Product)
        .from_previous()
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj: PurchaseSummary = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )

        domain_obj.reason = PurchaseSummaryReason.PAYMENT_CANCELLED

        snapshot_before = to_dto(domain_obj)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )
        assert snapshot_before == snapshot_after

    await uow_delete_and_check(model_type, domain_container.aggregate)


@pytest.mark.asyncio
async def test_product(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
    uow_delete_and_check: Callable[
        [Type[PersistableEntity], PersistableEntity], Awaitable[None]
    ],
) -> None:

    model_type: Type[PersistableEntity] = Product
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj: Product = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )

        domain_obj.price = domain_obj.price + 1

        snapshot_before = to_dto(domain_obj)
        uow.mark_commit()

    async with uow_check(model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )
        assert snapshot_before == snapshot_after

    await uow_delete_and_check(model_type, domain_container.aggregate)


@pytest.mark.asyncio
async def test_shipment(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
    uow_delete_and_check: Callable[
        [Type[PersistableEntity], PersistableEntity], Awaitable[None]
    ],
    domain_container: Container,
) -> None:

    shipment_container: AggregateContainer = await prepare_container(Shipment)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(Shipment)
        .from_id([shipment_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        shipment_cancel_service = domain_container.get(ShipmentCancelService)
        shipment: Shipment = resources.get_by_id(
            Shipment, shipment_container.aggregate.entity_id
        )

        shipment_summary: ShipmentSummary = shipment_cancel_service.cancel(shipment)
        resources.put(ShipmentSummary, shipment_summary)

        shipment_snapshot_before = to_dto(shipment)
        shipment_summary_snapshot_before = to_dto(shipment_summary)
        uow.mark_commit()

    async with uow_check(Shipment, shipment_container.aggregate) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(Shipment, shipment_container.aggregate.entity_id)
        )
        assert shipment_snapshot_before == snapshot_after

    async with uow_check(ShipmentSummary, shipment_summary) as uow2:
        resources = uow2.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(ShipmentSummary, shipment_summary.entity_id)
        )
        assert shipment_summary_snapshot_before == snapshot_after

    await uow_delete_and_check(Shipment, shipment_container.aggregate)
    await uow_delete_and_check(ShipmentSummary, shipment_summary)


@pytest.mark.asyncio
async def test_load_by_chlidren(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    uow_check: Callable[
        [Type[PersistableEntity], PersistableEntity], AsyncContextManager[UnitOfWork]
    ],
    uow_delete_and_check: Callable[
        [Type[PersistableEntity], PersistableEntity], Awaitable[None]
    ],
    product_container_factory: Callable[..., AggregateContainer],
) -> None:

    model_type: Type[PersistableEntity] = PurchaseDraft
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .load(Product)
        .from_previous()
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        domain_obj: PurchaseDraft = resources.get_by_id(
            model_type, domain_container.aggregate.entity_id
        )
        product = product_container_factory(name="test item", amount=10, price=1)
        other_product = product_container_factory(name="test item2", amount=20, price=2)
        resources.put(Product, product.aggregate)
        resources.put(Product, other_product.aggregate)
        domain_obj.add_item(product.aggregate.entity_id, 1)
        domain_obj.add_item(other_product.aggregate.entity_id, 2)

        snapshot_before = to_dto(domain_obj)
        uow.mark_commit()

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_attribute("items.product_id", [product.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow:
        resources = uow.get_resources()
        snapshot_after = to_dto(
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        )
        assert snapshot_before == snapshot_after
        assert len(snapshot_after.items) == 2

    await uow_delete_and_check(model_type, domain_container.aggregate)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_nowait(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
) -> None:

    model_type: Type[PersistableEntity] = PurchaseDraft
    domain_container: AggregateContainer = await prepare_container(model_type)

    class MyExc(Exception):
        pass

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow1:
        with pytest.raises(MyExc):
            async with uow_factory.create(
                QueryBuilder(mutating=True)
                .load(model_type)
                .from_id([domain_container.aggregate.entity_id])
                .for_update(no_wait=True)
                .build(),
                exception_on_nowait=MyExc,
            ) as uow2:
                pass


@pytest.mark.asyncio
@pytest.mark.integration
async def test_timeout(
    uow_factory: UnitOfWorkFactory,
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
) -> None:

    model_type: Type[PersistableEntity] = PurchaseDraft
    domain_container: AggregateContainer = await prepare_container(model_type)

    async with uow_factory.create(
        QueryBuilder(mutating=True)
        .load(model_type)
        .from_id([domain_container.aggregate.entity_id])
        .for_update()
        .build()
    ) as uow1:
        with pytest.raises(LockTimeoutException):
            async with uow_factory.create(
                QueryBuilder(mutating=True)
                .load(model_type)
                .from_id([domain_container.aggregate.entity_id])
                .for_update()
                .build(),
                wait_timeout_ms=300,
            ) as uow2:
                pass
