from typing import Any, Type
from sqlalchemy import tuple_
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import select, delete, insert, update

from shop_project.application.dto.purchase_active_dto import PurchaseActiveDTO
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.infrastructure.database.models.purchase_active import PurchaseActive as PurchaseActiveORM, PurchaseActiveItem as PurchaseActiveItemORM
from shop_project.shared.entity_id import EntityId

class PurchaseActiveRepository(BaseRepository[PurchaseActive]):
    model_type = PurchaseActive
    dto_type = PurchaseActiveDTO
    
    async def create(self, items: list[PurchaseActive]) -> None:
        """Создает список PurchaseActives и их order_items одним bulk-запросом."""
        if not items:
            return

        # --- PurchaseActives ---
        order_snapshots = [item.to_dict() for item in items]
        await self.session.execute(insert(PurchaseActiveORM), order_snapshots)

        # --- PurchaseActiveItems ---
        item_snapshots: list[dict[str, Any]] = []
        for order_snap in order_snapshots:
            purchase_active_id = order_snap["entity_id"]
            for item in order_snap.get("items", []):  # items — список словарей
                snap = item.copy()
                snap["purchase_active_id"] = purchase_active_id
                item_snapshots.append(snap)

        if item_snapshots:
            await self.session.execute(insert(PurchaseActiveItemORM), item_snapshots)

    async def update(self, items: list[PurchaseActive]) -> None:
        if not items:
            return

        order_snapshots = [item.to_dict() for item in items]
        order_ids = [snap["entity_id"] for snap in order_snapshots]

        order_fields = [f for f in order_snapshots[0].keys() if f != "items"]
        update_order_values = {
            field: self._build_bulk_update_case(field, order_snapshots, PurchaseActiveORM, ["entity_id"])
            for field in order_fields
        }
        await self.session.execute(
            update(PurchaseActiveORM)
            .where(PurchaseActiveORM.entity_id.in_(order_ids))
            .values(**update_order_values)
        )

        item_snapshots: list[dict[str, Any]] = []
        for snap in order_snapshots:
            for item in snap.get("items", []):
                snapshot = item.copy()
                snapshot["purchase_active_id"] = snap["entity_id"]
                item_snapshots.append(snapshot)

        await self._replace_children(
            session=self.session,
            root_id_name="purchase_active_id",
            root_ids=order_ids,
            child_model=PurchaseActiveItemORM,
            new_items=item_snapshots,
        )

    async def delete(self, items: list[PurchaseActive]) -> None:
        """Удаляет список PurchaseActives и их order_items одним bulk-запросом."""
        if not items:
            return

        # --- Удаляем сначала order_items ---
        ids = [item.entity_id.value for item in items]
        await self.session.execute(
            delete(PurchaseActiveItemORM).where(PurchaseActiveItemORM.purchase_active_id.in_(ids))
        )

        # --- Затем PurchaseActives ---
        await self.session.execute(
            delete(PurchaseActiveORM).where(PurchaseActiveORM.entity_id.in_(ids))
        )
    