from shop_project.domain.exceptions import DomainException
from shop_project.domain.services.inventory_service import InventoryService
from shop_project.domain.services.shipment_summary_service import ShipmentSummaryService
from shop_project.domain.shipment import Shipment
from shop_project.domain.shipment_summary import ShipmentSummary, ShipmentSummaryItem


class ShipmentReceiveService:
    def __init__(self, shipment_summary_service: ShipmentSummaryService, inventory_service: InventoryService) -> None:
        self._shipment_summary_service: ShipmentSummaryService = shipment_summary_service
        self._inventory_service: InventoryService = inventory_service
        
    def receive(self, shipment: Shipment) -> ShipmentSummary:
        if not shipment.is_active():
            raise DomainException('Order is not active')
        
        self._inventory_service.restock(shipment.get_items())
        
        return self._shipment_summary_service.finalize_receive(shipment)