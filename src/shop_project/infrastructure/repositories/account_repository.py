from sqlalchemy import select

from shop_project.application.dto.account_dto import AccountDTO
from shop_project.application.dto.mapper import to_domain
from shop_project.infrastructure.database.models.account import Account as AccountORM
from shop_project.infrastructure.entities.account import Account
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class AccountRepository(BaseRepository[Account, AccountDTO]):
    model_type = Account
    dto_type = AccountDTO

    async def create(self, items: list[AccountDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = AccountORM(**dto.model_dump())
            self.session.add(entity)

    async def update(self, items: list[AccountDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = self.session.identity_map.get(
                self._get_identity_key(AccountORM, dto.entity_id)
            )
            if not entity:
                continue

            entity.repopulate(**dto.model_dump())

    async def delete(self, items: list[AccountDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = await self.session.get(AccountORM, dto.entity_id)

            if not entity:
                raise RuntimeError(
                    f"Entity of type {self.model_type.__name__} {dto.entity_id} not found for deleting"
                )

            await self.session.delete(entity)

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

        return [to_domain(self.dto_type.model_validate(e)) for e in orm_entities]
