from decimal import Decimal
from typing import Any, Callable, Type
from shop_project.application.customer_order_service import CustomerOrderService
from shop_project.application.schemas.customer_order_schema import CreateCustomerOrderItemSchema, CreateCustomerOrderSchema
from shop_project.unit_of_work import UnitOfWork
from shop_project.domain.customer_order import CustomerOrder
from shop_project.domain.store_item import StoreItem
from shop_project.infrastructure.query.query_builder import QueryPlanBuilder
from shop_project.shared.entity_id import EntityId



def test_reserve(fake_uow_factory: Callable[[dict[Type[Any], list[Any]], str], UnitOfWork],
          rebuild_fake_uow: Callable[[UnitOfWork, str], UnitOfWork],
          potatoes_store_item_10: Callable[..., StoreItem],
          customer_order_factory: Callable[[], CustomerOrder]) -> None:
    potatoes = potatoes_store_item_10()
    customer_order = customer_order_factory()
    uow = fake_uow_factory({StoreItem: [potatoes]}, 'read_write')
    service = CustomerOrderService(uow)
    
    customer_order_schema = service.reserve_order(
        CreateCustomerOrderSchema.model_validate(customer_order.to_dict())
    )
    
    uow2 = rebuild_fake_uow(uow, 'read_only')
    
    uow2.set_query_plan(
        QueryPlanBuilder(mutating=False).load(CustomerOrder).from_id([customer_order_schema.entity_id]).no_lock()
        )
    
    with uow2:
        resources2 = uow2.get_resorces()
        customer_order_same = resources2.get_by_id(CustomerOrder, EntityId(customer_order_schema.entity_id))
        
        assert customer_order_same.state.value == 'RESERVED'
        assert customer_order_same.to_dict()['items'] == customer_order_schema.items

