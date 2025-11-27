from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import aliased, joinedload

from shop_project.application.dto.mapper import to_domain
from shop_project.application.dto.shipment_dto import ShipmentDTO
from shop_project.domain.entities.shipment import Shipment
from shop_project.infrastructure.database.models.shipment import (
    Shipment as ShipmentORM,
    ShipmentItem as ShipmentItemORM,
)
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class ShipmentRepository(BaseRepository[Shipment, ShipmentDTO]):
    model_type = Shipment
    dto_type = ShipmentDTO

    async def create(self, items: list[ShipmentDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = ShipmentORM(**dto.model_dump())
            self.session.add(entity)

            for child_dto in dto.items:
                child = ShipmentItemORM(
                    **child_dto.model_dump(), parent_id=entity.entity_id
                )
                child.parent_id = entity.entity_id
                self.session.add(child)

    async def update(self, items: list[ShipmentDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = self.session.identity_map.get(
                self._get_identity_key(ShipmentORM, dto.entity_id)
            )
            if not entity:
                continue

            entity.repopulate(**dto.model_dump())

            current_children: dict[tuple[UUID, UUID], ShipmentItemORM] = {
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
                    child = ShipmentItemORM(
                        **child_dto.model_dump(), parent_id=entity.entity_id
                    )
                    child.parent_id = entity.entity_id
                    self.session.add(child)

    async def delete(self, items: list[ShipmentDTO]) -> None:
        if not items:
            return

        for dto in items:
            entity = await self.session.get(ShipmentORM, dto.entity_id)

            if not entity:
                raise RuntimeError(
                    f"Entity of type {self.model_type.__name__} {dto.entity_id} not found for deleting"
                )

            for child in list(entity.items):
                await self.session.delete(child)

            await self.session.delete(entity)

    async def load(self, query: BaseQuery) -> list[Shipment]:
        if isinstance(query, ComposedQuery):
            item_alias = aliased(ShipmentItemORM, name="shipment_item")

            base_query = (
                select(ShipmentORM)
                .outerjoin(item_alias, ShipmentORM.items)
                .where(query.criteria.to_sqlalchemy(ShipmentORM))
                .options(joinedload(ShipmentORM.items))
            )
            base_query = self._apply_lock(
                base_query, query.lock, [ShipmentORM, item_alias]
            )
        elif isinstance(query, CustomQuery):
            base_query = query.compile_sqlalchemy()
        else:
            raise ValueError(f"Unknown query type: {type(query)}")

        result_raw = await self.session.execute(base_query)
        result_orm = result_raw.scalars().unique().all()
        result = [to_domain(self.dto_type.model_validate(item)) for item in result_orm]

        return result
