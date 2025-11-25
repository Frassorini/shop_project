from sqlalchemy import select
from sqlalchemy.sql import delete, insert, update

from shop_project.application.dto.account_dto import AccountDTO
from shop_project.application.dto.mapper import to_domain, to_dto
from shop_project.infrastructure.database.models.account import Account as AccountORM
from shop_project.infrastructure.entities.account import Account
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class AccountRepository(BaseRepository[Account]):
    model_type = Account
    dto_type = AccountDTO

    async def create(self, items: list[Account]) -> None:
        """Создает список Accounts одним bulk-запросом."""
        if not items:
            return

        values = [to_dto(item).model_dump() for item in items]
        print(values)
        await self.session.execute(insert(AccountORM), values)

    async def update(self, items: list[Account]) -> None:
        """Обновляет список Accounts одним bulk-запросом."""
        if not items:
            return

        snapshots = [to_dto(item).model_dump() for item in items]
        ids = [snap["entity_id"] for snap in snapshots]
        fields = snapshots[0].keys()

        update_values = {
            field: self._build_bulk_update_case(
                field, snapshots, AccountORM, ["entity_id"]
            )
            for field in fields
        }

        stmt = (
            update(AccountORM)
            .where(AccountORM.entity_id.in_(ids))
            .values(**update_values)
        )
        await self.session.execute(stmt)

    async def delete(self, items: list[Account]) -> None:
        """Удаляет список Accounts одним bulk_delete."""
        if not items:
            return

        ids = [item.entity_id for item in items]

        await self.session.execute(
            delete(AccountORM).where(AccountORM.entity_id.in_(ids))
        )

    async def load(self, query: BaseQuery) -> list[Account]:
        if isinstance(query, ComposedQuery):
            stmt = select(AccountORM).where(query.criteria.to_sqlalchemy(AccountORM))
            stmt = self._apply_lock(stmt, query.lock, [AccountORM])

        elif isinstance(query, CustomQuery):
            stmt = query.compile_sqlalchemy()

        else:
            raise ValueError(f"Unknown query type: {type(query)}")

        rows = await self.session.execute(stmt)
        orm_entities = rows.scalars().unique().all()

        return [to_domain(self.dto_type.model_validate(e)) for e in orm_entities]  # type: ignore
