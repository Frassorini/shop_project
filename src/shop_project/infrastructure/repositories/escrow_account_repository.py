from typing import Any, Type
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import select, delete, insert, update

from shop_project.application.dto.escrow_account_dto import EscrowAccountDTO
from shop_project.domain.escrow_account import EscrowAccount
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository
from shop_project.infrastructure.database.models.escrow_account import EscrowAccount as EscrowAccountORM
from shop_project.shared.entity_id import EntityId

class EscrowAccountRepository(BaseRepository[EscrowAccount]):
    model_type = EscrowAccount
    dto_type = EscrowAccountDTO
    
    async def create(self, items: list[EscrowAccount]) -> None:
        """Создает список EscrowAccounts одним запросом через bulk_insert."""
        if not items:
            return

        values = [item.to_dict() for item in items]
        await self.session.execute(insert(EscrowAccountORM), values)
    
    async def update(self, items: list[EscrowAccount]) -> None:
        if not items:
            return

        snapshots = [item.to_dict() for item in items]
        ids = [snap["entity_id"] for snap in snapshots]
        fields = snapshots[0].keys()

        update_values = {field: self._build_bulk_update_case(field, snapshots, EscrowAccountORM, ["entity_id"]) for field in fields}

        stmt = (
            update(EscrowAccountORM)
            .where(EscrowAccountORM.entity_id.in_(ids))
            .values(**update_values)
        )
        await self.session.execute(stmt)

    async def delete(self, items: list[EscrowAccount]) -> None:
        """Удаляет список EscrowAccounts одним запросом через bulk_delete."""
        if not items:
            return
        
        ids = [item.entity_id.value for item in items]
        await self.session.execute(delete(EscrowAccountORM).where(EscrowAccountORM.entity_id.in_(ids)))
    