from sqlalchemy.sql import delete, insert, update

from shop_project.application.dto.customer_dto import CustomerDTO
from shop_project.domain.entities.customer import Customer
from shop_project.infrastructure.database.models.customer import Customer as CustomerORM
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    model_type = Customer
    dto_type = CustomerDTO

    async def create(self, items: list[Customer]) -> None:
        """Создает список Customers одним запросом через bulk_insert."""
        if not items:
            return

        values = [item.to_dict() for item in items]
        await self.session.execute(insert(CustomerORM), values)

    async def update(self, items: list[Customer]) -> None:
        """Обновляет список Stores одним bulk-запросом."""
        if not items:
            return

        snapshots = [item.to_dict() for item in items]
        ids = [snap["entity_id"] for snap in snapshots]
        fields = snapshots[0].keys()

        update_values = {
            field: self._build_bulk_update_case(
                field, snapshots, CustomerORM, ["entity_id"]
            )
            for field in fields
        }

        stmt = (
            update(CustomerORM)
            .where(CustomerORM.entity_id.in_(ids))
            .values(**update_values)
        )
        await self.session.execute(stmt)

    async def delete(self, items: list[Customer]) -> None:
        """Удаляет список Customers одним запросом через bulk_delete."""
        if not items:
            return

        ids = [item.entity_id for item in items]
        await self.session.execute(
            delete(CustomerORM).where(CustomerORM.entity_id.in_(ids))
        )
