from typing import Any, Type
from sqlalchemy import tuple_
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import select, delete, insert, update

from shop_project.application.dto.customer_order_dto import CustomerOrderDTO
from shop_project.infrastructure.query.base_load_query import BaseLoadQuery
from shop_project.infrastructure.query.domain_load_query import DomainLoadQuery
from shop_project.infrastructure.query.prebuilt_load_query import PrebuiltLoadQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository
from shop_project.domain.customer_order import CustomerOrder
from shop_project.infrastructure.database.models.customer_order import CustomerOrder as CustomerOrderORM, CustomerOrderItem as CustomerOrderItemORM
from shop_project.shared.entity_id import EntityId

class CustomerOrderRepository(BaseRepository[CustomerOrder]):
    model_type = CustomerOrder
    dto_type = CustomerOrderDTO
    
    async def create(self, items: list[CustomerOrder]) -> None:
        """Создает список CustomerOrders и их order_items одним bulk-запросом."""
        if not items:
            return

        # --- CustomerOrders ---
        order_snapshots = [item.to_dict() for item in items]
        await self.session.execute(insert(CustomerOrderORM), order_snapshots)

        # --- CustomerOrderItems ---
        item_snapshots: list[dict[str, Any]] = []
        for order_snap in order_snapshots:
            customer_order_id = order_snap["entity_id"]
            for item in order_snap.get("items", []):  # items — список словарей
                snap = item.copy()
                snap["customer_order_id"] = customer_order_id
                item_snapshots.append(snap)

        if item_snapshots:
            await self.session.execute(insert(CustomerOrderItemORM), item_snapshots)

    async def update(self, items: list[CustomerOrder]) -> None:
        """Обновляет CustomerOrders и их order_items одним bulk-запросом."""
        if not items:
            return

        # --- Подготовка snapshots ---
        order_snapshots = [item.to_dict() for item in items]
        order_ids = [snap["entity_id"] for snap in order_snapshots]
        order_fields = order_snapshots[0].keys()

        # --- Обновление CustomerOrders ---
        update_order_values = {
            field: self._build_bulk_update_case(field, order_snapshots, CustomerOrderORM, ["entity_id"])
            for field in order_fields if field not in ["items"]
        }

        stmt_orders = (
            update(CustomerOrderORM)
            .where(CustomerOrderORM.entity_id.in_(order_ids))
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
                field: self._build_bulk_update_case(field, item_snapshots, CustomerOrderItemORM, pk_fields)
                for field in item_fields
            }

            # WHERE (customer_order_id, store_item_id) IN ((...), (...), ...)
            pk_tuples = {tuple(snap[pk] for pk in pk_fields) for snap in item_snapshots}
            ids_filter = tuple_(*(getattr(CustomerOrderItemORM, pk) for pk in pk_fields)).in_(pk_tuples)

            stmt_items = (
                update(CustomerOrderItemORM)
                .where(ids_filter)
                .values(**update_item_values)
            )
            await self.session.execute(stmt_items)



    async def delete(self, items: list[CustomerOrder]) -> None:
        """Удаляет список CustomerOrders и их order_items одним bulk-запросом."""
        if not items:
            return

        # --- Удаляем сначала order_items ---
        ids = [item.entity_id.value for item in items]
        await self.session.execute(
            delete(CustomerOrderItemORM).where(CustomerOrderItemORM.customer_order_id.in_(ids))
        )

        # --- Затем CustomerOrders ---
        await self.session.execute(
            delete(CustomerOrderORM).where(CustomerOrderORM.entity_id.in_(ids))
        )
    