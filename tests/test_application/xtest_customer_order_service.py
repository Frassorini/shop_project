from decimal import Decimal
from typing import Any, Callable, Type
from shop_project.application.customer_order_service import PurchaseActiveService
from shop_project.application.schemas.customer_order_schema import CreatePurchaseActiveItemSchema, CreatePurchaseActiveSchema
from shop_project.unit_of_work import UnitOfWork
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.product import Product
from shop_project.infrastructure.query.query_builder import QueryPlanBuilder
from shop_project.shared.entity_id import EntityId



def test_reserve(fake_uow_factory: Callable[[dict[Type[Any], list[Any]], str], UnitOfWork],
          rebuild_fake_uow: Callable[[UnitOfWork, str], UnitOfWork],
          potatoes_product_10: Callable[..., Product],
          customer_order_factory: Callable[[], PurchaseActive]) -> None:
    potatoes = potatoes_product_10()
    customer_order = customer_order_factory()
    uow = fake_uow_factory({Product: [potatoes]}, 'read_write')
    service = PurchaseActiveService(uow)
    
    customer_order_schema = service.reserve_order(
        CreatePurchaseActiveSchema.model_validate(customer_order.to_dict())
    )
    
    uow2 = rebuild_fake_uow(uow, 'read_only')
    
    uow2.set_query_plan(
        QueryPlanBuilder(mutating=False).load(PurchaseActive).from_id([customer_order_schema.entity_id]).no_lock()
        )
    
    with uow2:
        resources2 = uow2.get_resorces()
        customer_order_same = resources2.get_by_id(PurchaseActive, EntityId(customer_order_schema.entity_id))
        
        assert customer_order_same.state.value == 'RESERVED'
        assert customer_order_same.to_dict()['items'] == customer_order_schema.items

