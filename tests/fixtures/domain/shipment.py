from typing import Callable

import pytest
from dishka.container import Container

from shop_project.domain.entities.product import Product
from shop_project.domain.entities.shipment import Shipment
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.shipment_activation_service import (
    ShipmentActivationService,
    ShipmentRequest,
)
from tests.helpers import AggregateContainer


@pytest.fixture
def shipment_factory(
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    domain_container: Container,
) -> Callable[[], Shipment]:
    def factory() -> Shipment:
        shipment_activation_service = domain_container.get(ShipmentActivationService)
        request: ShipmentRequest = ShipmentRequest()
        potatoes = potatoes_product_10()
        sausages = sausages_product_10()
        request.add_item(potatoes.entity_id, 10)
        request.add_item(sausages.entity_id, 10)

        product_inventory = ProductInventory(stock=[potatoes, sausages])

        shipment: Shipment = shipment_activation_service.activate(
            product_inventory, request
        )

        return shipment

    return factory


@pytest.fixture
def shipment_container_factory(
    potatoes_product_10: Callable[[], Product],
    sausages_product_10: Callable[[], Product],
    domain_container: Container,
) -> Callable[[], AggregateContainer]:
    def factory() -> AggregateContainer:
        shipment_activation_service = domain_container.get(ShipmentActivationService)

        request: ShipmentRequest = ShipmentRequest()
        potatoes = potatoes_product_10()
        sausages = sausages_product_10()
        request.add_item(potatoes.entity_id, 10)
        request.add_item(sausages.entity_id, 10)

        product_inventory = ProductInventory(stock=[potatoes, sausages])

        shipment: Shipment = shipment_activation_service.activate(
            product_inventory, request
        )

        container: AggregateContainer = AggregateContainer(
            aggregate=shipment, dependencies={Product: [potatoes, sausages]}
        )

        return container

    return factory
