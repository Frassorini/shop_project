from sqlalchemy.sql import delete, insert, update

from shop_project.application.dto.manager_dto import ManagerDTO
from shop_project.application.dto.mapper import to_dto
from shop_project.domain.entities.manager import Manager
from shop_project.infrastructure.database.models.manager import Manager as ManagerORM
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class ManagerRepository(BaseRepository[Manager]):
    model_type = Manager
    dto_type = ManagerDTO

    async def create(self, items: list[Manager]) -> None:
        """Создает список Managers одним запросом через bulk_insert."""
        if not items:
            return

        values = [to_dto(item).model_dump() for item in items]
        await self.session.execute(insert(ManagerORM), values)

    async def update(self, items: list[Manager]) -> None:
        """Обновляет список Stores одним bulk-запросом."""
        if not items:
            return

        snapshots = [to_dto(item).model_dump() for item in items]
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

    async def delete(self, items: list[Manager]) -> None:
        """Удаляет список Managers одним запросом через bulk_delete."""
        if not items:
            return

        ids = [item.entity_id for item in items]
        await self.session.execute(
            delete(ManagerORM).where(ManagerORM.entity_id.in_(ids))
        )
