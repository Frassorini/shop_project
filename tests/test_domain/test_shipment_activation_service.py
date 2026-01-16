from typing import Callable

from dishka.container import Container

from shop_project.domain.entities.product import Product
from shop_project.domain.entities.shipment import Shipment, ShipmentItem
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.shipment_activation_service import (
    ShipmentActivationService,
    ShipmentRequest,
)


def test_activate(
    potatoes_product_10: Callable[[], Product],
    domain_container: Container,
) -> None:
    shipment_activation_service = domain_container.get(ShipmentActivationService)

    potatoes = potatoes_product_10()
    request: ShipmentRequest = ShipmentRequest()
    request.add_item(product_id=potatoes.entity_id, amount=2)
    product_inventory = ProductInventory([potatoes])

    shipment: Shipment = shipment_activation_service.activate(
        product_inventory=product_inventory, request=request
    )

    assert shipment.items == [ShipmentItem(potatoes.entity_id, 2)]
