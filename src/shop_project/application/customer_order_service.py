from shop_project.application.schemas.customer_order_schema import CreateCustomerOrderItemSchema, CreateCustomerOrderSchema, CustomerOrderSchema
from shop_project.unit_of_work import UnitOfWork

from shop_project.domain.customer_order import CustomerOrder
from shop_project.domain.store_item import StoreItem
from shop_project.domain.services.inventory_service import InventoryService
from shop_project.domain.services.reservation_service import ReservationService

from shop_project.infrastructure.query.query_builder import QueryPlanBuilder

from shop_project.shared.entity_id import EntityId


class CustomerOrderService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow
    
    def reserve_order(self, data: CreateCustomerOrderSchema,) -> CustomerOrderSchema:
        
        self.uow.set_query_plan(
            QueryPlanBuilder(mutating=True).load(StoreItem).from_id([item.store_item_id for item in data.items]).for_update()
        )
        
        with self.uow as uow:
            resources = uow.get_resorces()
            
            inventory_service = InventoryService(resources.get_all(StoreItem))
            reservation_service = ReservationService(inventory_service)
            
            order = CustomerOrder(customer_id=EntityId(data.customer_id),
                                  store_id=EntityId(data.store_id),
                                  entity_id=uow.get_unique_id(CustomerOrder)
            )
            
            resources.put(CustomerOrder, order)
            
            for item in data.items:
                order.add_item(store_item_id=EntityId(item.store_item_id),
                               amount=item.amount, 
                               price=resources.get_by_id(StoreItem, EntityId(item.store_item_id)).price, 
                               store_id=EntityId(data.store_id)
                )

            reservation_service.reserve_customer_order(order)
            
            uow.commit()
            
        return CustomerOrderSchema.model_validate(order.to_dict())

    def cancel_order(self, order_id: str) -> CustomerOrderSchema:
        self.uow.set_query_plan(
            QueryPlanBuilder(mutating=True)
            .load(CustomerOrder).from_id([order_id]).for_update()
            .load(StoreItem).from_previous().for_update()
        )
        
        with self.uow as uow:
            resources = uow.get_resorces()
            
            inventory_service = InventoryService(resources.get_all(StoreItem))
            reservation_service = ReservationService(inventory_service)
            
            order = resources.get_by_id(CustomerOrder, EntityId(order_id))
            
            reservation_service.cancel_customer_order(order)
            
            uow.commit()
            
        return CustomerOrderSchema.model_validate(order.to_dict())
