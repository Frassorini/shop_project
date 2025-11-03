from typing import Any, Callable, cast
import pytest

from shop_project.infrastructure.dependency_injection.domain.container import DomainContainer

from shop_project.domain.exceptions import DomainException
from shop_project.domain.product_inventory import ProductInventory
from shop_project.domain.services.shipment_receive_service import ShipmentReceiveService
from shop_project.domain.shipment_summary import ShipmentSummary, ShipmentSummaryReason
from shop_project.domain.product import Product
from shop_project.domain.shipment import Shipment, ShipmentItem
from shop_project.shared.entity_id import EntityId
from tests.helpers import AggregateContainer


def test_receive(shipment_conatiner_factory: Callable[[], AggregateContainer],
                 domain_container: DomainContainer,) -> None:
    shipment_receive_service = domain_container.shipment_receive_service()

    container = shipment_conatiner_factory()
    shipment: Shipment = cast(Shipment, container.aggregate)
    products: list[Product] = container.dependencies[Product]
    product_inventory = ProductInventory(products)

    products_snapshot = [item.to_dict() for item in products]
    shipment_summary: ShipmentSummary = shipment_receive_service.receive(product_inventory, shipment)
    products_snapshot_after = [item.to_dict() for item in products]
    
    difference = get_difference(products_snapshot, products_snapshot_after)
    
    for item in difference:
        assert item['difference'] == shipment_summary.get_item(EntityId(item['entity_id'])).amount
    
    assert shipment_summary.reason == ShipmentSummaryReason.RECEIVED
    

def get_difference(products_snapshot: list[Any], products_snapshot_after: list[Any]) -> list[Any]:
    difference: list[Any] = []

    for item in products_snapshot:
        for item_after in products_snapshot_after:
            if item['entity_id'] == item_after['entity_id']:
                difference.append({
                    'entity_id': item['entity_id'],
                    "difference": item_after['amount'] - item['amount']
                })
                break
    
    return difference