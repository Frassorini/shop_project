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

        # --- SupplierOrders ---
        order_snapshots = [item.to_dict() for item in items]
        await self.session.execute(insert(SupplierOrderORM), order_snapshots)

        # --- SupplierOrderItems ---
        item_snapshots: list[dict[str, Any]] = []
        for order_snap in order_snapshots:
            customer_order_id = order_snap["entity_id"]
            for item in order_snap.get("items", []):  # items — список словарей
                snap = item.copy()
                snap["customer_order_id"] = customer_order_id
                item_snapshots.append(snap)

        if item_snapshots:
            await self.session.execute(insert(SupplierOrderItemORM), item_snapshots)

    async def update(self, items: list[SupplierOrder]) -> None:
        """Обновляет SupplierOrders и их order_items одним bulk-запросом."""
        if not items:
            return

        # --- Подготовка snapshots ---
        order_snapshots = [item.to_dict() for item in items]
        order_ids = [snap["entity_id"] for snap in order_snapshots]
        order_fields = order_snapshots[0].keys()

        # --- Обновление SupplierOrders ---
        update_order_values = {
            field: self._build_bulk_update_case(field, order_snapshots, SupplierOrderORM, ["entity_id"])
            for field in order_fields if field not in ["items"]
        }

        stmt_orders = (
            update(SupplierOrderORM)
            .where(SupplierOrderORM.entity_id.in_(order_ids))
            .values(**update_order_values)
        )
        await self.session.execute(stmt_orders)

        # --- Разворачиваем order_items в один плоский список ---
        item_snapshots: list[dict[str, Any]] = []
        for order_snap in order_snapshots:
            customer_order_id = order_snap["entity_id"]
            for item in order_snap.get("items", []):  # items — список словарей
                snap = item.copy()
                snap["customer_order_id"] = customer_order_id  # добавляем связь с заказом
                item_snapshots.append(snap)

        if item_snapshots:
            pk_fields = ["customer_order_id", "store_item_id"]
            item_fields = [k for k in item_snapshots[0].keys() if k not in pk_fields]

            update_item_values = {
                field: self._build_bulk_update_case(field, item_snapshots, SupplierOrderItemORM, pk_fields)
                for field in item_fields
            }

            # WHERE (customer_order_id, store_item_id) IN ((...), (...), ...)
            pk_tuples = {tuple(snap[pk] for pk in pk_fields) for snap in item_snapshots}
            ids_filter = tuple_(*(getattr(SupplierOrderItemORM, pk) for pk in pk_fields)).in_(pk_tuples)

            stmt_items = (
                update(SupplierOrderItemORM)
                .where(ids_filter)
                .values(**update_item_values)
            )
            await self.session.execute(stmt_items)



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
    