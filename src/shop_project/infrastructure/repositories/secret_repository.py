from sqlalchemy import select

from shop_project.application.dto.mapper import to_domain
from shop_project.application.dto.secret_dto import SecretDTO
from shop_project.infrastructure.database.models.secret import Secret as SecretORM
from shop_project.infrastructure.entities.secret import Secret
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class SecretRepository(BaseRepository[Secret, SecretDTO]):
    model_type = Secret
    dto_type = SecretDTO

    async def create(self, items: list[SecretDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = SecretORM(**dto.model_dump())
            self.session.add(entity)

    async def update(self, items: list[SecretDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = self.session.identity_map.get(
                self._get_identity_key(SecretORM, dto.entity_id)
            )
            if not entity:
                continue

            entity.repopulate(**dto.model_dump())

    async def delete(self, items: list[SecretDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = self.session.identity_map.get(
                self._get_identity_key(SecretORM, dto.entity_id)
            )

            if not entity:
                raise RuntimeError(
                    f"Entity of type {self.model_type.__name__} {dto.entity_id} not found for deleting"
                )

            await self.session.delete(entity)

    async def load(self, query: BaseQuery) -> list[Secret]:
        if isinstance(query, ComposedQuery):
            base_query = select(SecretORM).where(
                query.criteria.to_sqlalchemy(SecretORM)
            )
            base_query = self._apply_lock(base_query, query.lock, [SecretORM])
        elif isinstance(query, CustomQuery):
            base_query = query.compile_sqlalchemy()
        else:
            raise ValueError(f"Unknown query type: {type(query)}")

        result_raw = await self.session.execute(base_query)
        result_orm = result_raw.scalars().unique().all()
        result = [to_domain(self.dto_type.model_validate(item)) for item in result_orm]

        return result
