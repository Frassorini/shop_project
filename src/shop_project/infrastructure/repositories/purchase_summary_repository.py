from typing import Any, Type
from sqlalchemy import tuple_
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import select, delete, insert, update

from shop_project.application.dto.purchase_summary_dto import PurchaseSummaryDTO
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.infrastructure.database.models.purchase_summary import PurchaseSummary as PurchaseSummaryORM, PurchaseSummaryItem as PurchaseSummaryItemORM
from shop_project.shared.entity_id import EntityId

class PurchaseSummaryRepository(BaseRepository[PurchaseSummary]):
    model_type = PurchaseSummary
    dto_type = PurchaseSummaryDTO
    
    async def create(self, items: list[PurchaseSummary]) -> None:
        """Создает список PurchaseSummarys и их order_items одним bulk-запросом."""
        if not items:
            return

        # --- PurchaseSummarys ---
        order_snapshots = [item.to_dict() for item in items]
        await self.session.execute(insert(PurchaseSummaryORM), order_snapshots)

        # --- PurchaseSummaryItems ---
        item_snapshots: list[dict[str, Any]] = []
        for order_snap in order_snapshots:
            purchase_summary_id = order_snap["entity_id"]
            for item in order_snap.get("items", []):  # items — список словарей
                snap = item.copy()
                snap["purchase_summary_id"] = purchase_summary_id
                item_snapshots.append(snap)

        if item_snapshots:
            await self.session.execute(insert(PurchaseSummaryItemORM), item_snapshots)

    async def update(self, items: list[PurchaseSummary]) -> None:
        if not items:
            return

        order_snapshots = [item.to_dict() for item in items]
        order_ids = [snap["entity_id"] for snap in order_snapshots]

        order_fields = [f for f in order_snapshots[0].keys() if f != "items"]
        update_order_values = {
            field: self._build_bulk_update_case(field, order_snapshots, PurchaseSummaryORM, ["entity_id"])
            for field in order_fields
        }
        await self.session.execute(
            update(PurchaseSummaryORM)
            .where(PurchaseSummaryORM.entity_id.in_(order_ids))
            .values(**update_order_values)
        )

        item_snapshots: list[dict[str, Any]] = []
        for snap in order_snapshots:
            for item in snap.get("items", []):
                snapshot = item.copy()
                snapshot["purchase_summary_id"] = snap["entity_id"]
                item_snapshots.append(snapshot)

        await self._replace_children(
            session=self.session,
            root_id_name="purchase_summary_id",
            root_ids=order_ids,
            child_model=PurchaseSummaryItemORM,
            new_items=item_snapshots,
        )

    async def delete(self, items: list[PurchaseSummary]) -> None:
        """Удаляет список PurchaseSummarys и их order_items одним bulk-запросом."""
        if not items:
            return

        # --- Удаляем сначала order_items ---
        ids = [item.entity_id.value for item in items]
        await self.session.execute(
            delete(PurchaseSummaryItemORM).where(PurchaseSummaryItemORM.purchase_summary_id.in_(ids))
        )

        # --- Затем PurchaseSummarys ---
        await self.session.execute(
            delete(PurchaseSummaryORM).where(PurchaseSummaryORM.entity_id.in_(ids))
        )