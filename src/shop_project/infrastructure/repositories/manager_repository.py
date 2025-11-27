from sqlalchemy import select
from sqlalchemy.sql import delete, insert, update

from shop_project.application.dto.manager_dto import ManagerDTO
from shop_project.application.dto.mapper import to_domain
from shop_project.domain.entities.manager import Manager
from shop_project.infrastructure.database.models.manager import Manager as ManagerORM
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class ManagerRepository(BaseRepository[Manager, ManagerDTO]):
    model_type = Manager
    dto_type = ManagerDTO

    async def create(self, items: list[ManagerDTO]) -> None:
        """Создает список Managers одним запросом через bulk_insert."""
        if not items:
            return

        values = [item.model_dump() for item in items]
        await self.session.execute(insert(ManagerORM), values)

    async def update(self, items: list[ManagerDTO]) -> None:
        """Обновляет список Stores одним bulk-запросом."""
        if not items:
            return

        snapshots = [item.model_dump() for item in items]
        ids = [snap["entity_id"] for snap in snapshots]
        fields = snapshots[0].keys()

        update_values = {
            field: self._build_bulk_update_case(
                field, snapshots, ManagerORM, ["entity_id"]
            )
            for field in fields
        }

        stmt = (
            update(ManagerORM)
            .where(ManagerORM.entity_id.in_(ids))
            .values(**update_values)
        )
        await self.session.execute(stmt)

    async def delete(self, items: list[ManagerDTO]) -> None:
        """Удаляет список Managers одним запросом через bulk_delete."""
        if not items:
            return

        ids = [item.entity_id for item in items]
        await self.session.execute(
            delete(ManagerORM).where(ManagerORM.entity_id.in_(ids))
        )

    async def load(self, query: BaseQuery) -> list[Manager]:
        if isinstance(query, ComposedQuery):
            base_query = select(ManagerORM).where(
                query.criteria.to_sqlalchemy(ManagerORM)
            )
            base_query = self._apply_lock(base_query, query.lock, [ManagerORM])
        elif isinstance(query, CustomQuery):
            base_query = query.compile_sqlalchemy()
        else:
            raise ValueError(f"Unknown query type: {type(query)}")

        result_raw = await self.session.execute(base_query)
        result_orm = result_raw.scalars().unique().all()
        result = [to_domain(self.dto_type.model_validate(item)) for item in result_orm]

        return result
