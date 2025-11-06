from typing import Callable
import pytest

from dishka.container import Container

from shop_project.domain.exceptions import DomainException
from shop_project.domain.product_inventory import ProductInventory
from shop_project.domain.services.shipment_activation_service import ShipmentActivationService, ShipmentRequest
from shop_project.domain.product import Product
from shop_project.domain.shipment import Shipment, ShipmentItem


def test_activate(potatoes_product_10: Callable[[], Product],
                  di_container: Container,) -> None:
    shipment_activation_service = di_container.get(ShipmentActivationService)

    potatoes = potatoes_product_10()
    request: ShipmentRequest = ShipmentRequest()
    request.add_item(product_id=potatoes.entity_id, amount=2)
    product_inventory = ProductInventory([potatoes])

    shipment: Shipment = shipment_activation_service.activate(product_inventory=product_inventory, request=request)

    assert shipment.get_items() == [ShipmentItem(potatoes.entity_id, 2)]
