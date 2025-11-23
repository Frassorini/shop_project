from typing import Any

from sqlalchemy.sql import delete, insert, update

from shop_project.application.dto.mapper import to_dto
from shop_project.application.dto.shipment_summary_dto import ShipmentSummaryDTO
from shop_project.domain.entities.shipment_summary import ShipmentSummary
from shop_project.infrastructure.database.models.shipment_summary import (
    ShipmentSummary as ShipmentSummaryORM,
    ShipmentSummaryItem as ShipmentSummaryItemORM,
)
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class ShipmentSummaryRepository(BaseRepository[ShipmentSummary]):
    model_type = ShipmentSummary
    dto_type = ShipmentSummaryDTO

    async def create(self, items: list[ShipmentSummary]) -> None:
        if not items:
            return

        shipment_snapshots = [to_dto(item).model_dump() for item in items]
        await self.session.execute(insert(ShipmentSummaryORM), shipment_snapshots)

        item_snapshots: list[dict[str, Any]] = []
        for shipment_snapshot in shipment_snapshots:
            for item in shipment_snapshot.get("items", []):
                snapshot = item.copy()
                snapshot["shipment_summary_id"] = shipment_snapshot["entity_id"]
                item_snapshots.append(snapshot)

        if item_snapshots:
            await self.session.execute(insert(ShipmentSummaryItemORM), item_snapshots)

    async def update(self, items: list[ShipmentSummary]) -> None:
        if not items:
            return

        shipment_snapshots = [to_dto(item).model_dump() for item in items]
        shipment_ids = [snap["entity_id"] for snap in shipment_snapshots]

        shipment_fields = [f for f in shipment_snapshots[0].keys() if f != "items"]
        update_shipment_values = {
            field: self._build_bulk_update_case(
                field, shipment_snapshots, ShipmentSummaryORM, ["entity_id"]
            )
            for field in shipment_fields
        }
        await self.session.execute(
            update(ShipmentSummaryORM)
            .where(ShipmentSummaryORM.entity_id.in_(shipment_ids))
            .values(**update_shipment_values)
        )

        item_snapshots: list[dict[str, Any]] = []
        for snap in shipment_snapshots:
            for item in snap.get("items", []):
                snapshot = item.copy()
                snapshot["shipment_summary_id"] = snap["entity_id"]
                item_snapshots.append(snapshot)

        await self._replace_children(
            session=self.session,
            root_id_name="shipment_summary_id",
            root_ids=shipment_ids,
            child_model=ShipmentSummaryItemORM,
            new_items=item_snapshots,
        )

    async def delete(self, items: list[ShipmentSummary]) -> None:
        if not items:
            return

        # --- Удаляем сначала shipment_items ---
        ids = [item.entity_id for item in items]
        await self.session.execute(
            delete(ShipmentSummaryItemORM).where(
                ShipmentSummaryItemORM.shipment_summary_id.in_(ids)
            )
        )

        # --- Затем SupplierOrders ---
        await self.session.execute(
            delete(ShipmentSummaryORM).where(ShipmentSummaryORM.entity_id.in_(ids))
        )
