from typing import Any, Callable, cast

from dishka.container import Container

from shop_project.application.shared.dto.mapper import to_dto
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.shipment import Shipment
from shop_project.domain.entities.shipment_summary import (
    ShipmentSummary,
    ShipmentSummaryReason,
)
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.shipment_receive_service import ShipmentReceiveService
from tests.helpers import AggregateContainer


def test_receive(
    shipment_conatiner_factory: Callable[[], AggregateContainer],
    domain_container: Container,
) -> None:
    shipment_receive_service = domain_container.get(ShipmentReceiveService)

    container = shipment_conatiner_factory()
    shipment: Shipment = cast(Shipment, container.aggregate)
    products: list[Product] = container.dependencies[Product]
    product_inventory = ProductInventory(products)

    products_snapshot = [to_dto(item).model_dump() for item in products]
    shipment_summary: ShipmentSummary = shipment_receive_service.receive(
        product_inventory, shipment
    )
    products_snapshot_after = [to_dto(item).model_dump() for item in products]

    difference = get_difference(products_snapshot, products_snapshot_after)

    for item in difference:
        assert item["difference"] == shipment_summary.get_item(item["entity_id"]).amount

    assert shipment_summary.reason == ShipmentSummaryReason.RECEIVED


def get_difference(
    products_snapshot: list[Any], products_snapshot_after: list[Any]
) -> list[Any]:
    difference: list[Any] = []

    for item in products_snapshot:
        for item_after in products_snapshot_after:
            if item["entity_id"] == item_after["entity_id"]:
                difference.append(
                    {
                        "entity_id": item["entity_id"],
                        "difference": item_after["amount"] - item["amount"],
                    }
                )
                break

    return difference
