from typing import Any, Callable, Coroutine, Literal, Type, TypeVar
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.customer import Customer
from shop_project.domain.customer_order import CustomerOrder
from shop_project.domain.store import Store
from shop_project.domain.supplier_order import SupplierOrder
from shop_project.domain.cart import Cart
from shop_project.domain.store_item import StoreItem

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.query.query_builder import QueryPlanBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWork
from shop_project.exceptions import UnitOfWorkException, ResourcesException


DomainObject = TypeVar('DomainObject', bound=BaseAggregate)


@pytest.mark.asyncio
@pytest.mark.parametrize('model_type', [Customer, StoreItem, Store, CustomerOrder, SupplierOrder, Cart],)
async def test_create(model_type: Type[DomainObject],
                domain_object_factory: Callable[[Type[DomainObject]], DomainObject],
                test_db_in_memory: Database,
                uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],) -> None:
    domain_object: DomainObject = domain_object_factory(model_type)
    uow: UnitOfWork = uow_factory(test_db_in_memory.get_session(), 'read_write')
    
    async with uow:
        resources = uow.get_resorces()
        
        resources.put(model_type, domain_object)
        
        await uow.commit()
    
    uow2: UnitOfWork = uow_factory(test_db_in_memory.get_session(), 'read_only')
    
    uow2.set_query_plan(
        QueryPlanBuilder(mutating=False).load(model_type).from_id([domain_object.entity_id.value]).no_lock()
        )
    
    async with uow2:
        resources2 = uow2.get_resorces()
        
        assert resources2.get_by_id(model_type, domain_object.entity_id)


@pytest.mark.asyncio
@pytest.mark.parametrize('model_type', [Customer, StoreItem, Store, CustomerOrder, SupplierOrder, Cart],)
async def test_update(model_type: Type[DomainObject], 
                domain_object_factory: Callable[[Type[DomainObject]], DomainObject],
                test_db_in_memory: Database,
                uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                mutate_domain_object: Callable[[DomainObject], DomainObject],
                fill_database: Callable[[Database, dict[Type[BaseAggregate], list[BaseAggregate]]], Coroutine[None, None, Database]]) -> None:
    domain_object: DomainObject = domain_object_factory(model_type)

    await fill_database(test_db_in_memory, {model_type: [domain_object]})
    uow: UnitOfWork = uow_factory(test_db_in_memory.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(model_type).from_id([domain_object.entity_id.value]).for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        domain_obj_from_db: DomainObject = resources.get_by_id(model_type, domain_object.entity_id)
        mutate_domain_object(domain_obj_from_db)
        snapshot_before = domain_obj_from_db.to_dict()
        await uow.commit()
    
    uow2: UnitOfWork = uow_factory(test_db_in_memory.get_session(), 'read_only')
    
    uow2.set_query_plan(
        QueryPlanBuilder(mutating=False).load(model_type).from_id([domain_object.entity_id.value]).no_lock()
        )
    
    async with uow2:
        resources2 = uow2.get_resorces()
        snapshot_after = resources2.get_by_id(model_type, domain_object.entity_id).to_dict()
    
    assert snapshot_before == snapshot_after
    
    
@pytest.mark.asyncio
@pytest.mark.parametrize('model_type', [Customer, StoreItem, Store, CustomerOrder, SupplierOrder, Cart],)
async def test_delete(model_type: Type[DomainObject], 
                domain_object_factory: Callable[[Type[DomainObject]], DomainObject],
                test_db_in_memory: Database,
                uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                fill_database: Callable[[Database, dict[Type[BaseAggregate], list[BaseAggregate]]], Coroutine[None, None, Database]],) -> None:
    domain_object: DomainObject = domain_object_factory(model_type)

    await fill_database(test_db_in_memory, {model_type: [domain_object]})
    uow: UnitOfWork = uow_factory(test_db_in_memory.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(model_type).from_id([domain_object.entity_id.value]).for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        
        domain_obj_from_db: DomainObject = resources.get_by_id(model_type, domain_object.entity_id)
        
        resources.delete(model_type, domain_obj_from_db)
        
        await uow.commit()
    
    uow2: UnitOfWork = uow_factory(test_db_in_memory.get_session(), 'read_only')
    
    uow2.set_query_plan(
        QueryPlanBuilder(mutating=False).load(model_type).from_id([domain_object.entity_id.value]).no_lock()
        )
    
    async with uow2:
        resources = uow.get_resorces()
        with pytest.raises(ResourcesException):
            assert resources.get_by_id(model_type, domain_object.entity_id) is None


@pytest.mark.asyncio
async def test_enter_uow_twice(domain_object_factory: Callable[[Type[DomainObject]], DomainObject],
                               test_db_in_memory: Database,
                               uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                               fill_database: Callable[[Database, dict[Type[BaseAggregate], list[BaseAggregate]]], Coroutine[None, None, Database]],) -> None:
    model_type: Type[Any] = Customer
    domain_object: DomainObject = domain_object_factory(model_type)

    await fill_database(test_db_in_memory, {model_type: [domain_object]})
    uow: UnitOfWork = uow_factory(test_db_in_memory.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(model_type).from_id([domain_object.entity_id.value]).for_update()
        )
    
    async with uow:
        uow.get_resorces()
    
    with pytest.raises(UnitOfWorkException):
        async with uow:
            pass

@pytest.mark.asyncio
async def test_complex_update(
                customer_order_factory: Callable[[], CustomerOrder],
                potatoes_store_item_10: Callable[[], StoreItem],
                test_db_in_memory: Database,
                uow_factory: Callable[[AsyncSession, Literal["read_write", "read_only"]], UnitOfWork],
                fill_database: Callable[[Database, dict[Type[BaseAggregate], list[BaseAggregate]]], Coroutine[None, None, Database]]) -> None:
    customer_order: CustomerOrder = customer_order_factory()
    potatoes = potatoes_store_item_10()

    await fill_database(test_db_in_memory, {CustomerOrder: [customer_order], StoreItem: [potatoes]})
    uow: UnitOfWork = uow_factory(test_db_in_memory.get_session(), 'read_write')
    
    uow.set_query_plan(
        QueryPlanBuilder(mutating=True).load(CustomerOrder).from_id([customer_order.entity_id.value]).for_update()
        )
    
    async with uow:
        resources = uow.get_resorces()
        domain_obj_from_db: CustomerOrder = resources.get_by_id(CustomerOrder, customer_order.entity_id)
        
        customer_order.add_item(potatoes.entity_id, potatoes.price, 1, potatoes.store_id)
        
        snapshot_before = domain_obj_from_db.to_dict()
        await uow.commit()
    
    uow2: UnitOfWork = uow_factory(test_db_in_memory.get_session(), 'read_only')
    
    uow2.set_query_plan(
        QueryPlanBuilder(mutating=False).load(CustomerOrder).from_id([customer_order.entity_id.value]).no_lock()
        )
    
    async with uow2:
        resources2 = uow2.get_resorces()
        snapshot_after = resources2.get_by_id(CustomerOrder, customer_order.entity_id).to_dict()
    
    assert snapshot_before == snapshot_after

