from sqlalchemy import select
from sqlalchemy.sql import delete, insert, update

from shop_project.application.dto.mapper import to_domain, to_dto
from shop_project.application.dto.product_dto import ProductDTO
from shop_project.domain.entities.product import Product
from shop_project.infrastructure.database.models.product import Product as ProductORM
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    model_type = Product
    dto_type = ProductDTO

    async def create(self, items: list[Product]) -> None:
        """Создает список Products одним запросом через bulk_insert."""
        if not items:
            return

        values = [to_dto(item).model_dump() for item in items]
        await self.session.execute(insert(ProductORM), values)

    async def update(self, items: list[Product]) -> None:
        """Обновляет список Stores одним bulk-запросом."""
        if not items:
            return

        snapshots = [to_dto(item).model_dump() for item in items]
        ids = [snap["entity_id"] for snap in snapshots]
        fields = snapshots[0].keys()

        update_values = {
            field: self._build_bulk_update_case(
                field, snapshots, ProductORM, ["entity_id"]
            )
            for field in fields
        }

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

        ids = [item.entity_id for item in items]
        await self.session.execute(
            delete(ProductORM).where(ProductORM.entity_id.in_(ids))
        )

    async def load(self, query: BaseQuery) -> list[Product]:
        if isinstance(query, ComposedQuery):
            base_query = select(ProductORM).where(
                query.criteria.to_sqlalchemy(ProductORM)
            )
            base_query = self._apply_lock(base_query, query.lock, [ProductORM])
        elif isinstance(query, CustomQuery):
            base_query = query.compile_sqlalchemy()
        else:
            raise ValueError(f"Unknown query type: {type(query)}")

        result_raw = await self.session.execute(base_query)
        result_orm = result_raw.scalars().unique().all()
        result = [to_domain(self.dto_type.model_validate(item)) for item in result_orm]

        return result  # type: ignore
