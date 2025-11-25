from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import aliased, joinedload
from sqlalchemy.sql import delete, insert, update

from shop_project.application.dto.mapper import to_domain, to_dto
from shop_project.application.dto.purchase_draft_dto import PurchaseDraftDTO
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.infrastructure.database.models.purchase_draft import (
    PurchaseDraft as PurchaseDraftORM,
    PurchaseDraftItem as PurchaseDraftItemORM,
)
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class PurchaseDraftRepository(BaseRepository[PurchaseDraft]):
    model_type = PurchaseDraft
    dto_type = PurchaseDraftDTO

    async def create(self, items: list[PurchaseDraft]) -> None:
        """Создает список PurchaseDrafts и их order_items одним bulk-запросом."""
        if not items:
            return

        # --- PurchaseDrafts ---
        order_snapshots = [to_dto(item).model_dump() for item in items]
        await self.session.execute(insert(PurchaseDraftORM), order_snapshots)

        # --- PurchaseDraftItems ---
        item_snapshots: list[dict[str, Any]] = []
        for order_snap in order_snapshots:
            purchase_draft_id = order_snap["entity_id"]
            for item in order_snap.get("items", []):  # items — список словарей
                snap = item.copy()
                snap["purchase_draft_id"] = purchase_draft_id
                item_snapshots.append(snap)

        if item_snapshots:
            await self.session.execute(insert(PurchaseDraftItemORM), item_snapshots)

    async def update(self, items: list[PurchaseDraft]) -> None:
        if not items:
            return

        order_snapshots = [to_dto(item).model_dump() for item in items]
        order_ids = [snap["entity_id"] for snap in order_snapshots]

        order_fields = [f for f in order_snapshots[0].keys() if f != "items"]
        update_order_values = {
            field: self._build_bulk_update_case(
                field, order_snapshots, PurchaseDraftORM, ["entity_id"]
            )
            for field in order_fields
        }
        await self.session.execute(
            update(PurchaseDraftORM)
            .where(PurchaseDraftORM.entity_id.in_(order_ids))
            .values(**update_order_values)
        )

        item_snapshots: list[dict[str, Any]] = []
        for snap in order_snapshots:
            for item in snap.get("items", []):
                snapshot = item.copy()
                snapshot["purchase_draft_id"] = snap["entity_id"]
                item_snapshots.append(snapshot)

        await self._replace_children(
            session=self.session,
            root_id_name="purchase_draft_id",
            root_ids=order_ids,
            child_model=PurchaseDraftItemORM,
            new_items=item_snapshots,
        )

    async def delete(self, items: list[PurchaseDraft]) -> None:
        """Удаляет список PurchaseDrafts и их order_items одним bulk-запросом."""
        if not items:
            return

        # --- Удаляем сначала order_items ---
        ids = [item.entity_id for item in items]
        await self.session.execute(
            delete(PurchaseDraftItemORM).where(
                PurchaseDraftItemORM.purchase_draft_id.in_(ids)
            )
        )

        # --- Затем PurchaseDrafts ---
        await self.session.execute(
            delete(PurchaseDraftORM).where(PurchaseDraftORM.entity_id.in_(ids))
        )

    async def load(self, query: BaseQuery) -> list[PurchaseDraft]:
        if isinstance(query, ComposedQuery):
            item_alias = aliased(PurchaseDraftItemORM, name="cart_item")

            base_query = (
                select(PurchaseDraftORM)
                .outerjoin(item_alias, PurchaseDraftORM.items)
                .where(query.criteria.to_sqlalchemy(PurchaseDraftORM))
                .options(joinedload(PurchaseDraftORM.items))
            )
            base_query = self._apply_lock(
                base_query, query.lock, [PurchaseDraftORM, item_alias]
            )
        elif isinstance(query, CustomQuery):
            base_query = query.compile_sqlalchemy()
        else:
            raise ValueError(f"Unknown query type: {type(query)}")

        result_raw = await self.session.execute(base_query)
        result_orm = result_raw.scalars().unique().all()
        result = [to_domain(self.dto_type.model_validate(item)) for item in result_orm]

        return result  # type: ignore
