from typing import Any, Callable, Type, TypeVar
import pytest

from domain.p_aggregate import PAggregate
from domain.customer import Customer
from domain.customer_order import CustomerOrder
from domain.supplier_order import SupplierOrder
from domain.cart import Cart
from domain.store_item import StoreItem

from infrastructure.query.query_plan import QueryPlan
from infrastructure.unit_of_work import UnitOfWork
from infrastructure.exceptions import UnitOfWorkException


DomainObject = TypeVar('DomainObject', bound=PAggregate)


@pytest.mark.parametrize('model_type', [Customer, SupplierOrder, Cart, CustomerOrder, StoreItem],)
def test_create(model_type: Type[DomainObject], 
                domain_object_factory: Callable[[Type[DomainObject]], DomainObject],
                fake_uow_factory: Callable[[dict[Type[Any], list[Any]]], UnitOfWork],
                rebuild_fake_uow: Callable[[UnitOfWork], UnitOfWork]) -> None:
    domain_object: DomainObject = domain_object_factory(model_type)
    uow: UnitOfWork = fake_uow_factory({})
    
    with uow:
        resources = uow.get_resorces()
        
        resources.put(model_type, domain_object)
        
        uow.commit()
    
    uow2: UnitOfWork = rebuild_fake_uow(uow)
    
    uow2.set_query_plan(
        QueryPlan().load(model_type).from_id([domain_object.entity_id])
        )
    
    with uow2:
        resources2 = uow2.get_resorces()
        
        assert resources2.get_by_id(model_type, domain_object.entity_id)


@pytest.mark.parametrize('model_type', [Customer, SupplierOrder, Cart, CustomerOrder, StoreItem],)
def test_update(model_type: Type[DomainObject], 
                domain_object_factory: Callable[[Type[DomainObject]], DomainObject],
                fake_uow_factory: Callable[[dict[Type[Any], list[Any]]], UnitOfWork],
                rebuild_fake_uow: Callable[[UnitOfWork], UnitOfWork],
                mutate_domain_object: Callable[[DomainObject], DomainObject]) -> None:
    domain_object: DomainObject = domain_object_factory(model_type)
    uow: UnitOfWork = fake_uow_factory({model_type: [domain_object]})
    
    uow.set_query_plan(
        QueryPlan().load(model_type).from_id([domain_object.entity_id])
        )
    
    with uow:
        resources = uow.get_resorces()
        domain_obj_from_db: DomainObject = resources.get_by_id(model_type, domain_object.entity_id)
        mutate_domain_object(domain_obj_from_db)
        snapshot_before = domain_obj_from_db.snapshot()
        uow.commit()
    
    uow2: UnitOfWork = rebuild_fake_uow(uow)
    
    uow2.set_query_plan(
        QueryPlan().load(model_type).from_id([domain_object.entity_id])
        )
    
    with uow2:
        resources2 = uow2.get_resorces()
        snapshot_after = resources2.get_by_id(model_type, domain_object.entity_id).snapshot()
    
    assert snapshot_before == snapshot_after
    

@pytest.mark.parametrize('model_type', [Customer, SupplierOrder, Cart, CustomerOrder, StoreItem],)
def test_delete(model_type: Type[DomainObject], 
                domain_object_factory: Callable[[Type[DomainObject]], DomainObject],
                fake_uow_factory: Callable[[dict[Type[Any], list[Any]]], UnitOfWork],
                rebuild_fake_uow: Callable[[UnitOfWork], UnitOfWork]) -> None:
    domain_object: DomainObject = domain_object_factory(model_type)
    uow: UnitOfWork = fake_uow_factory({model_type: [domain_object]})
    
    uow.set_query_plan(
        QueryPlan().load(model_type).from_id([domain_object.entity_id])
        )
    
    with uow:
        resources = uow.get_resorces()
        
        domain_obj_from_db: DomainObject = resources.get_by_id(model_type, domain_object.entity_id)
        
        resources.delete(model_type, domain_obj_from_db)
        
        uow.commit()
    
    uow2: UnitOfWork = rebuild_fake_uow(uow)
    
    uow2.set_query_plan(
        QueryPlan().load(model_type).from_id([domain_object.entity_id])
        )
    
    with pytest.raises(UnitOfWorkException):
        with uow2:
            pass
    