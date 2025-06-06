from domain.customer_order.model import CustomerOrder
from domain.exceptions import DomainException
from domain.store_item.inventory_service import InventoryService


class ReservationService():
    def __init__(self, inventory_service: InventoryService) -> None:
        self._inventory_service: InventoryService = inventory_service
        
    def reserve_customer_order(self, order: CustomerOrder) -> None:
        if not order.can_be_reserved():
            raise DomainException('Order cannot be reserved')
        
        self._inventory_service.reserve_stock(order.get_items())
        
        order.reserve()
    
    
    def cancel_customer_order(self, order: CustomerOrder) -> None:
        if not order.can_be_cancelled():
            raise DomainException('Order cannot be cancelled')
        
        self._inventory_service.restock(order.get_items())
        
        order.cancel()
    