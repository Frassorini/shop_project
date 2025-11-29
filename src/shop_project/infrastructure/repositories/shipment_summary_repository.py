from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import aliased, joinedload

from shop_project.application.dto.mapper import to_domain
from shop_project.application.dto.shipment_summary_dto import ShipmentSummaryDTO
from shop_project.domain.entities.shipment_summary import ShipmentSummary
from shop_project.infrastructure.database.models.shipment_summary import (
    ShipmentSummary as ShipmentSummaryORM,
    ShipmentSummaryItem as ShipmentSummaryItemORM,
)
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class ShipmentSummaryRepository(BaseRepository[ShipmentSummary, ShipmentSummaryDTO]):
    model_type = ShipmentSummary
    dto_type = ShipmentSummaryDTO

    async def create(self, items: list[ShipmentSummaryDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = ShipmentSummaryORM(**dto.model_dump())
            self.session.add(entity)

            for child_dto in dto.items:
                child = ShipmentSummaryItemORM(
                    **child_dto.model_dump(), parent_id=entity.entity_id
                )
                child.parent_id = entity.entity_id
                self.session.add(child)

    async def update(self, items: list[ShipmentSummaryDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = self.session.identity_map.get(
                self._get_identity_key(ShipmentSummaryORM, dto.entity_id)
            )
            if not entity:
                continue

            entity.repopulate(**dto.model_dump())

            current_children: dict[tuple[UUID, UUID], ShipmentSummaryItemORM] = {
                (child.parent_id, child.product_id): child for child in entity.items
            }

            for child in current_children.values():
                await self.session.delete(child)

            for child_dto in dto.items:
                key = (entity.entity_id, child_dto.product_id)
                if key in current_children:
                    current_children[key].repopulate(
                        **child_dto.model_dump(), parent_id=entity.entity_id
                    )
                    self.session.add(current_children[key])
                else:
                    child = ShipmentSummaryItemORM(
                        **child_dto.model_dump(), parent_id=entity.entity_id
                    )
                    child.parent_id = entity.entity_id
                    self.session.add(child)

    async def delete(self, items: list[ShipmentSummaryDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = self.session.identity_map.get(
                self._get_identity_key(ShipmentSummaryORM, dto.entity_id)
            )

            if not entity:
                raise RuntimeError(
                    f"Entity of type {self.model_type.__name__} {dto.entity_id} not found for deleting"
                )

            for child in list(entity.items):
                await self.session.delete(child)

            await self.session.delete(entity)

    async def load(self, query: BaseQuery) -> list[ShipmentSummary]:
        if isinstance(query, ComposedQuery):
            item_alias = aliased(ShipmentSummaryItemORM, name="shipment_summary_item")

            base_query = (
                select(ShipmentSummaryORM)
                .outerjoin(item_alias, ShipmentSummaryORM.items)
                .where(query.criteria.to_sqlalchemy(ShipmentSummaryORM))
                .options(joinedload(ShipmentSummaryORM.items))
            )
            base_query = self._apply_lock(
                base_query, query.lock, [ShipmentSummaryORM, item_alias]
            )
        elif isinstance(query, CustomQuery):
            base_query = query.compile_sqlalchemy()
        else:
            raise ValueError(f"Unknown query type: {type(query)}")

        result_raw = await self.session.execute(base_query)
        result_orm = result_raw.scalars().unique().all()
        result = [to_domain(self.dto_type.model_validate(item)) for item in result_orm]

        return result
