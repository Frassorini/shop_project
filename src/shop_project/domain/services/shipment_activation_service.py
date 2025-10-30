from shop_project.domain.exceptions import DomainException
from shop_project.domain.services.inventory_service import InventoryService
from shop_project.domain.services.shipment_summary_service import ShipmentSummaryService
from shop_project.domain.shipment import Shipment, ShipmentItem
from shop_project.shared.entity_id import EntityId


class ShipmentRequest:
    def __init__(self) -> None:
        self._items: list[ShipmentItem] = []
    
    def add_item(self, store_item_id: EntityId, amount: int) -> None:
        self._items.append(
            ShipmentItem(store_item_id, amount)
        )
        
    def get_items(self) -> list[ShipmentItem]:
        return self._items


class ShipmentActivationService:
    def __init__(self, inventory_service: InventoryService) -> None:
        self._inventory_service: InventoryService = inventory_service
        
    def activate(self, request: ShipmentRequest) -> Shipment:
        self._inventory_service.check_stock_validity(request.get_items())
        
        return Shipment(EntityId.get_random(), request.get_items())