from typing import Any, Type
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import select, delete, insert, update

from shop_project.application.dto.store_item_dto import StoreItemDTO
from shop_project.infrastructure.query.base_load_query import BaseLoadQuery
from shop_project.infrastructure.query.domain_load_query import DomainLoadQuery
from shop_project.infrastructure.query.prebuilt_load_query import PrebuiltLoadQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository
from shop_project.domain.store_item import StoreItem
from shop_project.infrastructure.database.models.store_item import StoreItem as StoreItemORM
from shop_project.shared.entity_id import EntityId

class StoreItemRepository(BaseRepository[StoreItem]):
    model_type = StoreItem
    dto_type = StoreItemDTO
    
    async def create(self, items: list[StoreItem]) -> None:
        """Создает список StoreItems одним запросом через bulk_insert."""
        if not items:
            return

        values = [item.to_dict() for item in items]
        await self.session.execute(insert(StoreItemORM), values)
    
    async def update(self, items: list[StoreItem]) -> None:
        """Обновляет список Stores одним bulk-запросом."""
        if not items:
            return

        snapshots = [item.to_dict() for item in items]
        ids = [snap["entity_id"] for snap in snapshots]
        fields = snapshots[0].keys()

        update_values = {field: self._build_bulk_update_case(field, snapshots, StoreItemORM, ["entity_id"]) for field in fields}

        stmt = (
            update(StoreItemORM)
            .where(StoreItemORM.entity_id.in_(ids))
            .values(**update_values)
        )
        await self.session.execute(stmt)

    async def delete(self, items: list[StoreItem]) -> None:
        """Удаляет список StoreItems одним запросом через bulk_delete."""
        if not items:
            return
        
        ids = [item.entity_id.value for item in items]
        await self.session.execute(delete(StoreItemORM).where(StoreItemORM.entity_id.in_(ids)))
    