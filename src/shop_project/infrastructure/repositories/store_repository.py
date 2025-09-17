from typing import Any, Type
from sqlalchemy import bindparam
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import select, delete, insert, update, case, and_

from shop_project.application.dto.store_dto import StoreDTO
from shop_project.application.dto.mapper import to_dto
from shop_project.infrastructure.query.base_load_query import BaseLoadQuery
from shop_project.infrastructure.query.domain_load_query import DomainLoadQuery
from shop_project.infrastructure.query.prebuilt_load_query import PrebuiltLoadQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository
from shop_project.domain.store import Store
from shop_project.infrastructure.database.models.store import Store as StoreORM
from shop_project.shared.entity_id import EntityId

class StoreRepository(BaseRepository[Store]):
    model_type = Store
    dto_type = StoreDTO
    
    async def create(self, items: list[Store]) -> None:
        """Создает список Stores одним запросом через bulk_insert."""
        if not items:
            return

        values = [item.to_dict() for item in items]
        await self.session.execute(insert(StoreORM), values)

    async def update(self, items: list[Store]) -> None:
        """Обновляет список Stores одним bulk-запросом."""
        if not items:
            return

        snapshots = [item.to_dict() for item in items]
        ids = [snap["entity_id"] for snap in snapshots]
        fields = snapshots[0].keys()

        update_values = {field: self._build_bulk_update_case(field, snapshots, StoreORM, ["entity_id"]) for field in fields}

        stmt = (
            update(StoreORM)
            .where(StoreORM.entity_id.in_(ids))
            .values(**update_values)
        )
        await self.session.execute(stmt)


    async def delete(self, items: list[Store]) -> None:
        """Удаляет список Stores одним запросом через bulk_delete."""
        if not items:
            return
        
        ids = [item.entity_id.value for item in items]
        await self.session.execute(delete(StoreORM).where(StoreORM.entity_id.in_(ids)))

    