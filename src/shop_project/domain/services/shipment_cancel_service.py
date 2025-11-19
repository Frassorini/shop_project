from shop_project.domain.exceptions import DomainException
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.shipment_summary_service import ShipmentSummaryService
from shop_project.domain.entities.shipment import Shipment
from shop_project.domain.entities.shipment_summary import ShipmentSummary, ShipmentSummaryItem


class ShipmentCancelService:
    def __init__(self, shipment_summary_service: ShipmentSummaryService) -> None:
        self._shipment_summary_service: ShipmentSummaryService = shipment_summary_service
        
    def cancel(self, shipment: Shipment) -> ShipmentSummary:
        if not shipment.is_active():
            raise DomainException('Order is not active')
        
        return self._shipment_summary_service.finalize_cancel(shipment)