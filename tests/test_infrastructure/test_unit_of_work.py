from decimal import Decimal
from typing import Any, Awaitable, Callable, Coroutine, Literal, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from shop_project.infrastructure.dependency_injection.domain.container import DomainContainer

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.customer import Customer
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.purchase_summary import PurchaseSummary
from shop_project.domain.escrow_account import EscrowAccount
from shop_project.domain.product import Product
from shop_project.domain.shipment import Shipment
from shop_project.domain.shipment_summary import ShipmentSummary

from shop_project.domain.services.purchase_claim_service import PurchaseClaimService
from shop_project.domain.services.shipment_cancel_service import ShipmentCancelService

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.query.query_builder import QueryPlanBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWork
from shop_project.exceptions import UnitOfWorkException, ResourcesException
from tests.helpers import AggregateContainer


@pytest.mark.asyncio
async def test_customer(test_db: Database,
                               uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                               prepare_container: Callable[[Type[BaseAggregate], Database], Coroutine[None, None, AggregateContainer]],
                               uow_check: Callable[..., Any],) -> None:
    model_type: Type[Any] = Customer
    domain_container: AggregateContainer = await prepare_container(model_type, test_db)
    uow: UnitOfWork = uow_factory(test_db.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(model_type).from_id([domain_container.aggregate.entity_id.value]).for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        domain_obj: Customer = resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        
        domain_obj.name = 'new name'
        
        snapshot_before = domain_obj.to_dict()
        await uow.commit()
    
    async with uow_check(uow_factory, test_db, model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resorces()
        snapshot_after = resources.get_by_id(model_type, domain_container.aggregate.entity_id).to_dict()
        assert snapshot_before == snapshot_after

    uow: UnitOfWork = uow_factory(test_db.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(model_type).from_id([domain_container.aggregate.entity_id.value]).for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        domain_obj_from_db: BaseAggregate = resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        resources.delete(model_type, domain_obj_from_db)
        await uow.commit()
    
    
    async with uow_check(uow_factory, test_db, model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resorces()
        with pytest.raises(ResourcesException):
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)


@pytest.mark.asyncio
async def test_purchase_draft(test_db: Database,
                           uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                           prepare_container: Callable[[Type[BaseAggregate], Database], Coroutine[None, None, AggregateContainer]],
                           uow_check: Callable[..., Any],
                           uow_delete_and_check: Callable[..., Awaitable[None]],
                           product_container_factory: Callable[..., AggregateContainer]) -> None:
    model_type: Type[Any] = PurchaseDraft
    domain_container: AggregateContainer = await prepare_container(model_type, test_db)
    uow: UnitOfWork = uow_factory(test_db.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True)
        .load(model_type).from_id([domain_container.aggregate.entity_id.value]).for_update()
        .load(Product).from_previous().for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        domain_obj: PurchaseDraft = resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        product = product_container_factory(
            name="test item", amount=10, price=1
        )
        resources.put(Product, product.aggregate)
        domain_obj.add_item(product.aggregate.entity_id, 1)
        
        snapshot_before = domain_obj.to_dict()
        await uow.commit()
    
    async with uow_check(uow_factory, test_db, model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resorces()
        snapshot_after = resources.get_by_id(model_type, domain_container.aggregate.entity_id).to_dict()
        assert snapshot_before == snapshot_after
    
    await uow_delete_and_check(uow_factory, test_db, model_type, domain_container.aggregate)


@pytest.mark.asyncio
async def test_uow_purchase_claim(test_db: Database,
                                     uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                                     prepare_container: Callable[[Type[BaseAggregate], Database], Coroutine[None, None, AggregateContainer]],
                                     uow_check: Callable[..., Any],
                                     uow_delete_and_check: Callable[..., Awaitable[None]],
                                     domain_container: DomainContainer,) -> None:
    purchase_active_container: AggregateContainer = await prepare_container(PurchaseActive, test_db)
    uow: UnitOfWork = uow_factory(test_db.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True)
        .load(PurchaseActive).from_id([purchase_active_container.aggregate.entity_id.value]).for_update()
        .load(EscrowAccount).from_previous().for_update()
        .load(Product).from_previous(0).for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        purchase_claim_service = domain_container[PurchaseClaimService]
        purchase_active: PurchaseActive = resources.get_by_id(PurchaseActive, purchase_active_container.aggregate.entity_id)
        escrow_account = resources.get_by_id(EscrowAccount, purchase_active.escrow_account_id)
        
        escrow_account.mark_as_paid()
        purchase_summary = purchase_claim_service.claim(purchase_active, escrow_account)
        resources.put(PurchaseSummary, purchase_summary)
        
        purchase_active_snapshot_before = purchase_active.to_dict()
        escrow_account_snapshot_before = escrow_account.to_dict()
        purchase_summary_snapshot_before = purchase_summary.to_dict()
        await uow.commit()
    
    async with uow_check(uow_factory, test_db, PurchaseActive, purchase_active) as uow2:
        resources = uow2.get_resorces()
        snapshot_after = resources.get_by_id(PurchaseActive, purchase_active.entity_id).to_dict()
        assert purchase_active_snapshot_before == snapshot_after
    
    async with uow_check(uow_factory, test_db, EscrowAccount, escrow_account) as uow2:
        resources = uow2.get_resorces()
        snapshot_after = resources.get_by_id(EscrowAccount, escrow_account.entity_id).to_dict()
        assert escrow_account_snapshot_before == snapshot_after
    
    async with uow_check(uow_factory, test_db, PurchaseSummary, purchase_summary) as uow2:
        resources = uow2.get_resorces()
        snapshot_after = resources.get_by_id(PurchaseSummary, purchase_summary.entity_id).to_dict()
        assert purchase_summary_snapshot_before == snapshot_after
        
        
    await uow_delete_and_check(uow_factory, test_db, PurchaseActive, purchase_active)
    await uow_delete_and_check(uow_factory, test_db, PurchaseSummary, purchase_summary)
    await uow_delete_and_check(uow_factory, test_db, EscrowAccount, escrow_account)


@pytest.mark.asyncio
async def test_product(test_db: Database,
                          uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                          prepare_container: Callable[[Type[BaseAggregate], Database], Coroutine[None, None, AggregateContainer]],
                          uow_check: Callable[..., Any],
                          uow_delete_and_check: Callable[..., Awaitable[None]],) -> None:
    model_type: Type[Any] = Product
    domain_container: AggregateContainer = await prepare_container(model_type, test_db)
    uow: UnitOfWork = uow_factory(test_db.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(model_type).from_id([domain_container.aggregate.entity_id.value]).for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        domain_obj: Product = resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        
        domain_obj.price = domain_obj.price + 1
        
        snapshot_before = domain_obj.to_dict()
        await uow.commit()
    
    async with uow_check(uow_factory, test_db, model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resorces()
        snapshot_after = resources.get_by_id(model_type, domain_container.aggregate.entity_id).to_dict()
        assert snapshot_before == snapshot_after

    await uow_delete_and_check(uow_factory, test_db, model_type, domain_container.aggregate)


@pytest.mark.asyncio
async def test_shipment(test_db: Database,
                                     uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                                     prepare_container: Callable[[Type[BaseAggregate], Database], Coroutine[None, None, AggregateContainer]],
                                     uow_check: Callable[..., Any],
                                     uow_delete_and_check: Callable[..., Awaitable[None]],
                                     domain_container: DomainContainer,) -> None:
    shipment_container: AggregateContainer = await prepare_container(Shipment, test_db)
    uow: UnitOfWork = uow_factory(test_db.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(Shipment).from_id([shipment_container.aggregate.entity_id.value]).for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        shipment_cancel_service = domain_container[ShipmentCancelService]
        shipment: Shipment = resources.get_by_id(Shipment, shipment_container.aggregate.entity_id)
        
        shipment_summary: ShipmentSummary = shipment_cancel_service.cancel(shipment)
        resources.put(ShipmentSummary, shipment_summary)
        
        shipment_snapshot_before = shipment.to_dict()
        shipment_summary_snapshot_before = shipment_summary.to_dict()
        await uow.commit()
    
    async with uow_check(uow_factory, test_db, Shipment, shipment_container.aggregate) as uow2:
        resources = uow2.get_resorces()
        snapshot_after = resources.get_by_id(Shipment, shipment_container.aggregate.entity_id).to_dict()
        assert shipment_snapshot_before == snapshot_after
    
    async with uow_check(uow_factory, test_db, ShipmentSummary, shipment_summary) as uow2:
        resources = uow2.get_resorces()
        snapshot_after = resources.get_by_id(ShipmentSummary, shipment_summary.entity_id).to_dict()
        assert shipment_summary_snapshot_before == snapshot_after
    
    await uow_delete_and_check(uow_factory, test_db, Shipment, shipment_container.aggregate)
    await uow_delete_and_check(uow_factory, test_db, ShipmentSummary, shipment_summary)


@pytest.mark.asyncio
async def test_enter_uow_twice(test_db: Database,
                               uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                               prepare_container: Callable[[Type[BaseAggregate], Database], Coroutine[None, None, AggregateContainer]]) -> None:
    model_type: Type[Any] = Customer
    domain_container: AggregateContainer = await prepare_container(model_type, test_db)

    uow: UnitOfWork = uow_factory(test_db.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(model_type).from_id([domain_container.aggregate.entity_id.value]).for_update()
        )
    
    async with uow:
        uow.get_resorces()
    
    with pytest.raises(UnitOfWorkException):
        async with uow:
            pass
