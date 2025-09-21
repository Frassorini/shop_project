from typing import Any, Type
from sqlalchemy import tuple_
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import select, delete, insert, update

from shop_project.application.dto.cart_dto import CartDTO
from shop_project.infrastructure.query.base_load_query import BaseLoadQuery
from shop_project.infrastructure.query.domain_load_query import DomainLoadQuery
from shop_project.infrastructure.query.prebuilt_load_query import PrebuiltLoadQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository
from shop_project.domain.cart import Cart
from shop_project.infrastructure.database.models.cart import Cart as CartORM, CartItem as CartItemORM
from shop_project.shared.entity_id import EntityId

class CartRepository(BaseRepository[Cart]):
    model_type = Cart
    dto_type = CartDTO
    
    async def create(self, items: list[Cart]) -> None:
        """Создает список Carts и их order_items одним bulk-запросом."""
        if not items:
            return

        # --- Carts ---
        order_snapshots = [item.to_dict() for item in items]
        await self.session.execute(insert(CartORM), order_snapshots)

        # --- CartItems ---
        item_snapshots: list[dict[str, Any]] = []
        for order_snap in order_snapshots:
            customer_order_id = order_snap["entity_id"]
            for item in order_snap.get("items", []):  # items — список словарей
                snap = item.copy()
                snap["customer_order_id"] = customer_order_id
                item_snapshots.append(snap)

        if item_snapshots:
            await self.session.execute(insert(CartItemORM), item_snapshots)

    async def update(self, items: list[Cart]) -> None:
        if not items:
            return

        order_snapshots = [item.to_dict() for item in items]
        order_ids = [snap["entity_id"] for snap in order_snapshots]

        order_fields = [f for f in order_snapshots[0].keys() if f != "items"]
        update_order_values = {
            field: self._build_bulk_update_case(field, order_snapshots, CartORM, ["entity_id"])
            for field in order_fields
        }
        await self.session.execute(
            update(CartORM)
            .where(CartORM.entity_id.in_(order_ids))
            .values(**update_order_values)
        )

        item_snapshots: list[dict[str, Any]] = []
        for snap in order_snapshots:
            for item in snap.get("items", []):
                snapshot = item.copy()
                snapshot["cart_id"] = snap["entity_id"]
                item_snapshots.append(snapshot)

        await self._replace_children(
            session=self.session,
            root_id_name="cart_id",
            root_ids=order_ids,
            child_model=CartItemORM,
            new_items=item_snapshots,
        )



    async def delete(self, items: list[Cart]) -> None:
        """Удаляет список Carts и их order_items одним bulk-запросом."""
        if not items:
            return

        # --- Удаляем сначала order_items ---
        ids = [item.entity_id.value for item in items]
        await self.session.execute(
            delete(CartItemORM).where(CartItemORM.cart_id.in_(ids))
        )

        # --- Затем Carts ---
        await self.session.execute(
            delete(CartORM).where(CartORM.entity_id.in_(ids))
        )
    