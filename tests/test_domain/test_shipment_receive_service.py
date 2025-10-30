from typing import Any, Callable, cast
import pytest

from shop_project.domain.exceptions import DomainException
from shop_project.domain.services.inventory_service import InventoryService
from shop_project.domain.services.shipment_receive_service import ShipmentReceiveService
from shop_project.domain.shipment_summary import ShipmentSummary, ShipmentSummaryReason
from shop_project.domain.store_item import StoreItem
from shop_project.domain.shipment import Shipment, ShipmentItem
from shop_project.shared.entity_id import EntityId
from tests.helpers import AggregateContainer


def test_(potatoes_store_item_10: Callable[[], StoreItem], 
          shipment_receive_service_factory: Callable[[InventoryService], ShipmentReceiveService]) -> None:
    potatoes = potatoes_store_item_10()
    inventory_service = InventoryService([potatoes])
    
    shipment_receive_service = shipment_receive_service_factory(inventory_service)


def test_receive(shipment_conatiner_factory: Callable[[], AggregateContainer],
                  shipment_receive_service_factory: Callable[[InventoryService], ShipmentReceiveService]) -> None:
    container = shipment_conatiner_factory()
    shipment: Shipment = cast(Shipment, container.aggregate)
    store_items: list[StoreItem] = container.dependencies[StoreItem]
    inventory_service = InventoryService(store_items)
    shipment_receive_service = shipment_receive_service_factory(inventory_service)

    store_items_snapshot = [item.to_dict() for item in store_items]
    shipment_summary: ShipmentSummary = shipment_receive_service.receive(shipment)
    store_items_snapshot_after = [item.to_dict() for item in store_items]
    
    difference = get_difference(store_items_snapshot, store_items_snapshot_after)
    
    for item in difference:
        assert item['difference'] == shipment_summary.get_item(EntityId(item['entity_id'])).amount
    
    assert shipment_summary.reason == ShipmentSummaryReason.RECEIVED
    

def get_difference(store_items_snapshot: list[Any], store_items_snapshot_after: list[Any]) -> list[Any]:
    difference: list[Any] = []

    for item in store_items_snapshot:
        for item_after in store_items_snapshot_after:
            if item['entity_id'] == item_after['entity_id']:
                difference.append({
                    'entity_id': item['entity_id'],
                    "difference": item_after['amount'] - item['amount']
                })
                break
    
    return difference