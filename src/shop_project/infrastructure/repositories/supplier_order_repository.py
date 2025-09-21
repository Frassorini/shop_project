from typing import Any, Type
from sqlalchemy import tuple_
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import select, delete, insert, update

from shop_project.application.dto.supplier_order_dto import SupplierOrderDTO
from shop_project.infrastructure.query.base_load_query import BaseLoadQuery
from shop_project.infrastructure.query.domain_load_query import DomainLoadQuery
from shop_project.infrastructure.query.prebuilt_load_query import PrebuiltLoadQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository
from shop_project.domain.supplier_order import SupplierOrder
from shop_project.infrastructure.database.models.supplier_order import SupplierOrder as SupplierOrderORM, SupplierOrderItem as SupplierOrderItemORM
from shop_project.shared.entity_id import EntityId

class SupplierOrderRepository(BaseRepository[SupplierOrder]):
    model_type = SupplierOrder
    dto_type = SupplierOrderDTO
    
    async def create(self, items: list[SupplierOrder]) -> None:
        """Создает список SupplierOrders и их order_items одним bulk-запросом."""
        if not items:
            return

        order_snapshots = [item.to_dict() for item in items]
        await self.session.execute(insert(SupplierOrderORM), order_snapshots)

        item_snapshots: list[dict[str, Any]] = []
        for order_snapshot in order_snapshots:
            for item in order_snapshot.get("items", []):
                snapshot = item.copy()
                snapshot["supplier_order_id"] = order_snapshot["entity_id"]
                item_snapshots.append(snapshot)

        if item_snapshots:
            await self.session.execute(insert(SupplierOrderItemORM), item_snapshots)

    async def update(self, items: list[SupplierOrder]) -> None:
        if not items:
            return

        order_snapshots = [item.to_dict() for item in items]
        order_ids = [snap["entity_id"] for snap in order_snapshots]

        order_fields = [f for f in order_snapshots[0].keys() if f != "items"]
        update_order_values = {
            field: self._build_bulk_update_case(field, order_snapshots, SupplierOrderORM, ["entity_id"])
            for field in order_fields
        }
        await self.session.execute(
            update(SupplierOrderORM)
            .where(SupplierOrderORM.entity_id.in_(order_ids))
            .values(**update_order_values)
        )

        item_snapshots: list[dict[str, Any]] = []
        for snap in order_snapshots:
            for item in snap.get("items", []):
                snapshot = item.copy()
                snapshot["supplier_order_id"] = snap["entity_id"]
                item_snapshots.append(snapshot)

        await self._replace_children(
            session=self.session,
            root_id_name="supplier_order_id",
            root_ids=order_ids,
            child_model=SupplierOrderItemORM,
            new_items=item_snapshots,
        )

    async def delete(self, items: list[SupplierOrder]) -> None:
        """Удаляет список SupplierOrders и их order_items одним bulk-запросом."""
        if not items:
            return

        # --- Удаляем сначала order_items ---
        ids = [item.entity_id.value for item in items]
        await self.session.execute(
            delete(SupplierOrderItemORM).where(SupplierOrderItemORM.supplier_order_id.in_(ids))
        )

        # --- Затем SupplierOrders ---
        await self.session.execute(
            delete(SupplierOrderORM).where(SupplierOrderORM.entity_id.in_(ids))
        )
    