from typing import Any

from sqlalchemy.sql import delete, insert, update

from shop_project.application.dto.shipment_dto import ShipmentDTO
from shop_project.domain.entities.shipment import Shipment
from shop_project.infrastructure.database.models.shipment import (
    Shipment as ShipmentORM,
    ShipmentItem as ShipmentItemORM,
)
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class ShipmentRepository(BaseRepository[Shipment]):
    model_type = Shipment
    dto_type = ShipmentDTO

    async def create(self, items: list[Shipment]) -> None:
        if not items:
            return

        shipment_snapshots = [item.to_dict() for item in items]
        await self.session.execute(insert(ShipmentORM), shipment_snapshots)

        item_snapshots: list[dict[str, Any]] = []
        for shipment_snapshot in shipment_snapshots:
            for item in shipment_snapshot.get("items", []):
                snapshot = item.copy()
                snapshot["shipment_id"] = shipment_snapshot["entity_id"]
                item_snapshots.append(snapshot)

        if item_snapshots:
            await self.session.execute(insert(ShipmentItemORM), item_snapshots)

    async def update(self, items: list[Shipment]) -> None:
        if not items:
            return

        shipment_snapshots = [item.to_dict() for item in items]
        shipment_ids = [snap["entity_id"] for snap in shipment_snapshots]

        shipment_fields = [f for f in shipment_snapshots[0].keys() if f != "items"]
        update_shipment_values = {
            field: self._build_bulk_update_case(
                field, shipment_snapshots, ShipmentORM, ["entity_id"]
            )
            for field in shipment_fields
        }
        await self.session.execute(
            update(ShipmentORM)
            .where(ShipmentORM.entity_id.in_(shipment_ids))
            .values(**update_shipment_values)
        )

        item_snapshots: list[dict[str, Any]] = []
        for snap in shipment_snapshots:
            for item in snap.get("items", []):
                snapshot = item.copy()
                snapshot["shipment_id"] = snap["entity_id"]
                item_snapshots.append(snapshot)

        await self._replace_children(
            session=self.session,
            root_id_name="shipment_id",
            root_ids=shipment_ids,
            child_model=ShipmentItemORM,
            new_items=item_snapshots,
        )

    async def delete(self, items: list[Shipment]) -> None:
        if not items:
            return

        # --- Удаляем сначала shipment_items ---
        ids = [item.entity_id.value for item in items]
        await self.session.execute(
            delete(ShipmentItemORM).where(ShipmentItemORM.shipment_id.in_(ids))
        )

        # --- Затем SupplierOrders ---
        await self.session.execute(
            delete(ShipmentORM).where(ShipmentORM.entity_id.in_(ids))
        )
