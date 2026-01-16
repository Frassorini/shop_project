from uuid import uuid4

from shop_project.domain.entities.shipment import Shipment
from shop_project.domain.entities.shipment_summary import (
    ShipmentSummary,
    ShipmentSummaryItem,
    ShipmentSummaryReason,
)
from shop_project.domain.exceptions import DomainInvalidStateError


class ShipmentSummaryService:
    def __init__(self) -> None:
        pass

    def finalize_receive(self, shipment: Shipment) -> ShipmentSummary:
        return self._finalize(shipment, ShipmentSummaryReason.RECEIVED)

    def finalize_cancel(self, shipment: Shipment) -> ShipmentSummary:
        return self._finalize(shipment, ShipmentSummaryReason.CANCELLED)

    def _finalize(
        self, shipment: Shipment, reason: ShipmentSummaryReason
    ) -> ShipmentSummary:
        if shipment.is_finalized():
            raise DomainInvalidStateError("Cannot finalize finalized shipment")

        shipment_summary_items: list[ShipmentSummaryItem] = []

        for item in shipment.items:
            shipment_summary_items.append(
                ShipmentSummaryItem(
                    product_id=item.product_id,
                    amount=item.amount,
                )
            )

        shipment_summary = ShipmentSummary(
            entity_id=uuid4(), reason=reason, items=shipment_summary_items
        )

        shipment.finalize()

        return shipment_summary
