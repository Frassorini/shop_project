from uuid import UUID, uuid4

from shop_project.domain.entities.shipment import Shipment, ShipmentItem
from shop_project.domain.helpers.product_inventory import ProductInventory


class ShipmentRequest:
    def __init__(self) -> None:
        self._items: list[ShipmentItem] = []

    def add_item(self, product_id: UUID, amount: int) -> None:
        self._items.append(ShipmentItem(product_id, amount))

    def get_items(self) -> list[ShipmentItem]:
        return self._items


class ShipmentActivationService:
    def activate(
        self, product_inventory: ProductInventory, request: ShipmentRequest
    ) -> Shipment:
        product_inventory.check_stock_validity(request.get_items())

        return Shipment(uuid4(), request.get_items())
