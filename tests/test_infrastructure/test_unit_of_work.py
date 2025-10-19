from decimal import Decimal
from typing import Any, Callable, Coroutine, Literal, Type, TypeVar
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.customer import Customer
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.store import Store
from shop_project.domain.supplier_order import SupplierOrder
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.store_item import StoreItem

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.query.query_builder import QueryPlanBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWork
from shop_project.exceptions import UnitOfWorkException, ResourcesException
from tests.helpers import AggregateContainer


DomainObject = TypeVar('DomainObject', bound=BaseAggregate)


@pytest.mark.asyncio
@pytest.mark.parametrize('model_type', [Customer, StoreItem, Store, PurchaseActive, SupplierOrder, PurchaseDraft],)
async def test_create_delete(model_type: Type[DomainObject], 
                test_db: Database,
                uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                prepare_container: Callable[[Type[DomainObject], Database], Coroutine[None, None, AggregateContainer]],
                uow_check: Callable[..., Any],) -> None:
    domain_container: AggregateContainer = await prepare_container(model_type, test_db)
    uow: UnitOfWork = uow_factory(test_db.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(model_type).from_id([domain_container.aggregate.entity_id.value]).for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        domain_obj_from_db: DomainObject = resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        resources.delete(model_type, domain_obj_from_db)
        await uow.commit()
    
    
    async with uow_check(uow_factory, test_db, model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resorces()
        with pytest.raises(ResourcesException):
            resources.get_by_id(model_type, domain_container.aggregate.entity_id)


@pytest.mark.asyncio
async def test_update_customer(test_db: Database,
                               uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                               prepare_container: Callable[[Type[DomainObject], Database], Coroutine[None, None, AggregateContainer]],
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


@pytest.mark.asyncio
async def test_update_store(test_db: Database,
                               uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                               prepare_container: Callable[[Type[DomainObject], Database], Coroutine[None, None, AggregateContainer]],
                               uow_check: Callable[..., Any],) -> None:
    model_type: Type[Any] = Store
    domain_container: AggregateContainer = await prepare_container(model_type, test_db)
    uow: UnitOfWork = uow_factory(test_db.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(model_type).from_id([domain_container.aggregate.entity_id.value]).for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        domain_obj: Store = resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        
        domain_obj.name = 'new name'
        
        snapshot_before = domain_obj.to_dict()
        await uow.commit()
    
    async with uow_check(uow_factory, test_db, model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resorces()
        snapshot_after = resources.get_by_id(model_type, domain_container.aggregate.entity_id).to_dict()
        assert snapshot_before == snapshot_after


@pytest.mark.asyncio
async def test_update_store_item(test_db: Database,
                               uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                               prepare_container: Callable[[Type[DomainObject], Database], Coroutine[None, None, AggregateContainer]],
                               uow_check: Callable[..., Any],) -> None:
    model_type: Type[Any] = StoreItem
    domain_container: AggregateContainer = await prepare_container(model_type, test_db)
    uow: UnitOfWork = uow_factory(test_db.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(model_type).from_id([domain_container.aggregate.entity_id.value]).for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        domain_obj: StoreItem = resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        
        domain_obj.price = domain_obj.price + 1
        
        snapshot_before = domain_obj.to_dict()
        await uow.commit()
    
    async with uow_check(uow_factory, test_db, model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resorces()
        snapshot_after = resources.get_by_id(model_type, domain_container.aggregate.entity_id).to_dict()
        assert snapshot_before == snapshot_after


@pytest.mark.asyncio
async def test_update_customer_order(test_db: Database,
                                     uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                                     prepare_container: Callable[[Type[DomainObject], Database], Coroutine[None, None, AggregateContainer]],
                                     uow_check: Callable[..., Any],
                                     store_item_container_factory: Callable[..., AggregateContainer]) -> None:
    model_type: Type[Any] = PurchaseActive
    domain_container: AggregateContainer = await prepare_container(model_type, test_db)
    uow: UnitOfWork = uow_factory(test_db.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(model_type).from_id([domain_container.aggregate.entity_id.value]).for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        domain_obj: PurchaseActive = resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        store_item = store_item_container_factory(
            name="test item", amount=10, store=domain_container.dependencies[Store][0], price=1
        )
        resources.put(StoreItem, store_item.aggregate)
        domain_obj.add_item(store_item.aggregate.entity_id, Decimal(1), 1, domain_obj.store_id)
        
        snapshot_before = domain_obj.to_dict()
        await uow.commit()
    
    async with uow_check(uow_factory, test_db, model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resorces()
        snapshot_after = resources.get_by_id(model_type, domain_container.aggregate.entity_id).to_dict()
        assert snapshot_before == snapshot_after


@pytest.mark.asyncio
async def test_update_supplier_order(test_db: Database,
                                     uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                                     prepare_container: Callable[[Type[DomainObject], Database], Coroutine[None, None, AggregateContainer]],
                                     uow_check: Callable[..., Any],
                                     store_item_container_factory: Callable[..., AggregateContainer]) -> None:
    model_type: Type[Any] = SupplierOrder
    domain_container: AggregateContainer = await prepare_container(model_type, test_db)
    uow: UnitOfWork = uow_factory(test_db.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(model_type).from_id([domain_container.aggregate.entity_id.value]).for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        domain_obj: SupplierOrder = resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        store_item = store_item_container_factory(
            name="test item", amount=10, store=domain_container.dependencies[Store][0], price=1
        )
        resources.put(StoreItem, store_item.aggregate)
        domain_obj.add_item(store_item.aggregate.entity_id, 1, domain_obj.store_id)
        
        snapshot_before = domain_obj.to_dict()
        await uow.commit()
    
    async with uow_check(uow_factory, test_db, model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resorces()
        snapshot_after = resources.get_by_id(model_type, domain_container.aggregate.entity_id).to_dict()
        assert snapshot_before == snapshot_after


@pytest.mark.asyncio
async def test_update_cart(test_db: Database,
                           uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                           prepare_container: Callable[[Type[DomainObject], Database], Coroutine[None, None, AggregateContainer]],
                           uow_check: Callable[..., Any],
                           store_item_container_factory: Callable[..., AggregateContainer]) -> None:
    model_type: Type[Any] = PurchaseDraft
    domain_container: AggregateContainer = await prepare_container(model_type, test_db)
    uow: UnitOfWork = uow_factory(test_db.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(model_type).from_id([domain_container.aggregate.entity_id.value]).for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        domain_obj: PurchaseDraft = resources.get_by_id(model_type, domain_container.aggregate.entity_id)
        store_item = store_item_container_factory(
            name="test item", amount=10, store=domain_container.dependencies[Store][0], price=1
        )
        resources.put(StoreItem, store_item.aggregate)
        domain_obj.add_item(store_item.aggregate.entity_id, 1, domain_obj.store_id)
        
        snapshot_before = domain_obj.to_dict()
        await uow.commit()
    
    async with uow_check(uow_factory, test_db, model_type, domain_container.aggregate) as uow2:
        resources = uow2.get_resorces()
        snapshot_after = resources.get_by_id(model_type, domain_container.aggregate.entity_id).to_dict()
        assert snapshot_before == snapshot_after


@pytest.mark.asyncio
async def test_enter_uow_twice(domain_object_factory: Callable[[Type[DomainObject]], AggregateContainer],
                               test_db: Database,
                               uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                               prepare_container: Callable[[Type[DomainObject], Database], Coroutine[None, None, AggregateContainer]]) -> None:
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


@pytest.fixture
def uow_check() -> Callable[..., Any]:
    def _check(uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
               test_db: Database, 
               model_type: Type[BaseAggregate], 
               domain_object: BaseAggregate) -> UnitOfWork:
        uow = uow_factory(test_db.get_session(), 'read_only')
        uow.set_query_plan(
            QueryPlanBuilder(mutating=False)
            .load(model_type)
            .from_id([domain_object.entity_id.value])
            .no_lock()
        )
        return uow
    return _check


@pytest.fixture
def prepare_container(domain_object_factory: Callable[[Type[DomainObject]], AggregateContainer], 
                            fill_database: Callable[[Database, dict[Type[BaseAggregate], list[BaseAggregate]]], Coroutine[None, None, Database]]
                            ) -> Callable[[Type[DomainObject], Database], Coroutine[None, None, AggregateContainer]]:
    async def _prepare(model_type: Type[DomainObject], test_db: Database) -> AggregateContainer:
        domain_container = domain_object_factory(model_type)
        to_fill = domain_container.dependencies.copy()

        to_fill.setdefault(model_type, []).append(domain_container.aggregate)
        await fill_database(test_db, to_fill)

        return domain_container
    return _prepare
