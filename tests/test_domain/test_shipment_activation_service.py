from typing import Callable
import pytest

from shop_project.domain.exceptions import DomainException
from shop_project.domain.services.inventory_service import InventoryService
from shop_project.domain.services.shipment_activation_service import ShipmentActivationService, ShipmentRequest
from shop_project.domain.store_item import StoreItem
from shop_project.domain.shipment import Shipment, ShipmentItem


def test_(potatoes_store_item_10: Callable[[], StoreItem], 
          shipment_activation_service_factory: Callable[[InventoryService], ShipmentActivationService]) -> None:
    potatoes = potatoes_store_item_10()
    inventory_service = InventoryService([potatoes])
    
    shipment_activation_service = shipment_activation_service_factory(inventory_service)


def test_activate(potatoes_store_item_10: Callable[[], StoreItem],
                  shipment_activation_service_factory: Callable[[InventoryService], ShipmentActivationService]) -> None:
    potatoes = potatoes_store_item_10()
    request: ShipmentRequest = ShipmentRequest()
    request.add_item(store_item_id=potatoes.entity_id, amount=2)
    inventory_service = InventoryService([potatoes])
    shipment_activation_service = shipment_activation_service_factory(inventory_service)

    shipment: Shipment = shipment_activation_service.activate(request)

    assert shipment.get_items() == [ShipmentItem(potatoes.entity_id, 2)]
