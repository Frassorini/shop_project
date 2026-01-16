from shop_project.domain.entities.shipment import Shipment
from shop_project.domain.entities.shipment_summary import ShipmentSummary
from shop_project.domain.exceptions import DomainInvalidStateError
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.shipment_summary_service import ShipmentSummaryService


class ShipmentReceiveService:
    def __init__(self, shipment_summary_service: ShipmentSummaryService) -> None:
        self._shipment_summary_service: ShipmentSummaryService = (
            shipment_summary_service
        )

    def receive(
        self, product_inventory: ProductInventory, shipment: Shipment
    ) -> ShipmentSummary:
        if not shipment.is_active():
            raise DomainInvalidStateError("Cannot receive inactive shipment")

        product_inventory.restock(shipment.items)

        return self._shipment_summary_service.finalize_receive(shipment)
