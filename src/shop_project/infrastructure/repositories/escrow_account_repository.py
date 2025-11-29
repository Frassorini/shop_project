from sqlalchemy import select

from shop_project.application.dto.escrow_account_dto import EscrowAccountDTO
from shop_project.application.dto.mapper import to_domain
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.infrastructure.database.models.escrow_account import (
    EscrowAccount as EscrowAccountORM,
)
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class EscrowAccountRepository(BaseRepository[EscrowAccount, EscrowAccountDTO]):
    model_type = EscrowAccount
    dto_type = EscrowAccountDTO

    async def create(self, items: list[EscrowAccountDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = EscrowAccountORM(**dto.model_dump())
            self.session.add(entity)

    async def update(self, items: list[EscrowAccountDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = self.session.identity_map.get(
                self._get_identity_key(EscrowAccountORM, dto.entity_id)
            )
            if not entity:
                continue

            entity.repopulate(**dto.model_dump())

    async def delete(self, items: list[EscrowAccountDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = self.session.identity_map.get(
                self._get_identity_key(EscrowAccountORM, dto.entity_id)
            )

            if not entity:
                raise RuntimeError(
                    f"Entity of type {self.model_type.__name__} {dto.entity_id} not found for deleting"
                )

            await self.session.delete(entity)

    async def load(self, query: BaseQuery) -> list[EscrowAccount]:
        if isinstance(query, ComposedQuery):
            base_query = select(EscrowAccountORM).where(
                query.criteria.to_sqlalchemy(EscrowAccountORM)
            )
            base_query = self._apply_lock(base_query, query.lock, [EscrowAccountORM])
        elif isinstance(query, CustomQuery):
            base_query = query.compile_sqlalchemy()
        else:
            raise ValueError(f"Unknown query type: {type(query)}")

        result_raw = await self.session.execute(base_query)
        result_orm = result_raw.scalars().unique().all()
        result = [to_domain(self.dto_type.model_validate(item)) for item in result_orm]

        return result
