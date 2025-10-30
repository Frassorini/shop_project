from datetime import datetime, timezone
from typing import Callable

import pytest

from shop_project.domain.services.shipment_activation_service import ShipmentActivationService, ShipmentRequest
from shop_project.domain.product import Product
from shop_project.shared.entity_id import EntityId
from shop_project.domain.shipment import Shipment
from tests.fixtures.domain.purchase_active import InventoryService
from tests.helpers import AggregateContainer


@pytest.fixture
def shipment_factory(
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    shipment_activation_service_factory: Callable[[InventoryService], ShipmentActivationService],
) -> Callable[[], Shipment]:
    def factory() -> Shipment:
        request: ShipmentRequest = ShipmentRequest()
        potatoes = potatoes_product_10()
        sausages = sausages_product_10()
        request.add_item(potatoes.entity_id, 10)
        request.add_item(sausages.entity_id, 10)
        
        inventory_service = InventoryService(stock=[potatoes, sausages])
        shipment_activation_service = shipment_activation_service_factory(inventory_service)
        
        shipment: Shipment = shipment_activation_service.activate(request)
        
        return shipment
    return factory


@pytest.fixture
def shipment_conatiner_factory(
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    shipment_activation_service_factory: Callable[[InventoryService], ShipmentActivationService],
) -> Callable[[], AggregateContainer]:
    def factory() -> AggregateContainer:
        request: ShipmentRequest = ShipmentRequest()
        potatoes = potatoes_product_10()
        sausages = sausages_product_10()
        request.add_item(potatoes.entity_id, 10)
        request.add_item(sausages.entity_id, 10)
        
        inventory_service = InventoryService(stock=[potatoes, sausages])
        shipment_activation_service = shipment_activation_service_factory(inventory_service)
        
        shipment: Shipment = shipment_activation_service.activate(request)
        
        container: AggregateContainer = AggregateContainer(
            aggregate=shipment, 
            dependencies={Product: [potatoes, sausages]})
        
        return container
    return factory
