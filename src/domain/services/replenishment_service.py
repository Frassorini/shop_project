from domain.exceptions import DomainException
from domain.store_item.inventory_service import InventoryService
from domain.supplier_order.model import SupplierOrder


class ReplenishmentService:
    def __init__(self, inventory_service: InventoryService) -> None:
        self._inventory_service: InventoryService = inventory_service
        
    def replenish(self, order: SupplierOrder) -> None:
        if not order.can_be_received():
            raise DomainException('Order cannot be replenished')
        
        self._inventory_service.restock(order.get_items())
        
        order.receive()