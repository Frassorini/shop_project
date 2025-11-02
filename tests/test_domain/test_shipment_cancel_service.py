from typing import Any, Callable, cast
import pytest

from shop_project.domain.exceptions import DomainException
from shop_project.domain.product_inventory import ProductInventory
from shop_project.domain.services.shipment_cancel_service import ShipmentCancelService
from shop_project.domain.shipment_summary import ShipmentSummary, ShipmentSummaryReason
from shop_project.domain.product import Product
from shop_project.domain.shipment import Shipment, ShipmentItem
from shop_project.shared.entity_id import EntityId
from tests.helpers import AggregateContainer


def test_(potatoes_product_10: Callable[[], Product], 
          shipment_cancel_service_factory: Callable[[], ShipmentCancelService]) -> None:
    potatoes = potatoes_product_10()
    product_inventory = ProductInventory([potatoes])
    
    shipment_cancel_service = shipment_cancel_service_factory()


def test_cancel(shipment_conatiner_factory: Callable[[], AggregateContainer],
                  shipment_cancel_service_factory: Callable[[], ShipmentCancelService]) -> None:
    container = shipment_conatiner_factory()
    shipment: Shipment = cast(Shipment, container.aggregate)
    products: list[Product] = container.dependencies[Product]
    shipment_cancel_service = shipment_cancel_service_factory()

    products_snapshot = [item.to_dict() for item in products]
    shipment_summary: ShipmentSummary = shipment_cancel_service.cancel(shipment)
    products_snapshot_after = [item.to_dict() for item in products]
    
    difference = get_difference(products_snapshot, products_snapshot_after)
    
    for item in difference:
        assert item['difference'] == 0

    assert shipment_summary.reason == ShipmentSummaryReason.CANCELLED


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