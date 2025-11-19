from typing import Any, Type
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import select, delete, insert, update

from shop_project.application.dto.product_dto import ProductDTO
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository
from shop_project.domain.product import Product
from shop_project.infrastructure.database.models.product import Product as ProductORM
from shop_project.shared.entity_id import EntityId

class ProductRepository(BaseRepository[Product]):
    model_type = Product
    dto_type = ProductDTO
    
    async def create(self, items: list[Product]) -> None:
        """Создает список Products одним запросом через bulk_insert."""
        if not items:
            return

        values = [item.to_dict() for item in items]
        await self.session.execute(insert(ProductORM), values)
    
    async def update(self, items: list[Product]) -> None:
        """Обновляет список Stores одним bulk-запросом."""
        if not items:
            return

        snapshots = [item.to_dict() for item in items]
        ids = [snap["entity_id"] for snap in snapshots]
        fields = snapshots[0].keys()

        update_values = {field: self._build_bulk_update_case(field, snapshots, ProductORM, ["entity_id"]) for field in fields}

        stmt = (
            update(ProductORM)
            .where(ProductORM.entity_id.in_(ids))
            .values(**update_values)
        )
        await self.session.execute(stmt)

    async def delete(self, items: list[Product]) -> None:
        """Удаляет список Products одним запросом через bulk_delete."""
        if not items:
            return
        
        ids = [item.entity_id.value for item in items]
        await self.session.execute(delete(ProductORM).where(ProductORM.entity_id.in_(ids)))
    