from sqlalchemy import select
from sqlalchemy.sql import delete, insert, update

from shop_project.application.dto.employee_dto import EmployeeDTO
from shop_project.application.dto.mapper import to_domain, to_dto
from shop_project.domain.entities.employee import Employee
from shop_project.infrastructure.database.models.employee import Employee as EmployeeORM
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    model_type = Employee
    dto_type = EmployeeDTO

    async def create(self, items: list[Employee]) -> None:
        """Создает список Employees одним запросом через bulk_insert."""
        if not items:
            return

        values = [to_dto(item).model_dump() for item in items]
        await self.session.execute(insert(EmployeeORM), values)

    async def update(self, items: list[Employee]) -> None:
        """Обновляет список Stores одним bulk-запросом."""
        if not items:
            return

        snapshots = [to_dto(item).model_dump() for item in items]
        ids = [snap["entity_id"] for snap in snapshots]
        fields = snapshots[0].keys()

        update_values = {
            field: self._build_bulk_update_case(
                field, snapshots, EmployeeORM, ["entity_id"]
            )
            for field in fields
        }

        stmt = (
            update(EmployeeORM)
            .where(EmployeeORM.entity_id.in_(ids))
            .values(**update_values)
        )
        await self.session.execute(stmt)

    async def delete(self, items: list[Employee]) -> None:
        """Удаляет список Employees одним запросом через bulk_delete."""
        if not items:
            return

        ids = [item.entity_id for item in items]
        await self.session.execute(
            delete(EmployeeORM).where(EmployeeORM.entity_id.in_(ids))
        )

    async def load(self, query: BaseQuery) -> list[Employee]:
        if isinstance(query, ComposedQuery):
            base_query = select(EmployeeORM).where(
                query.criteria.to_sqlalchemy(EmployeeORM)
            )
            base_query = self._apply_lock(base_query, query.lock, [EmployeeORM])
        elif isinstance(query, CustomQuery):
            base_query = query.compile_sqlalchemy()
        else:
            raise ValueError(f"Unknown query type: {type(query)}")

        result_raw = await self.session.execute(base_query)
        result_orm = result_raw.scalars().unique().all()
        result = [to_domain(self.dto_type.model_validate(item)) for item in result_orm]

        return result  # type: ignore
