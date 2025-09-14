from typing import Any
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import select, delete, insert, update
from shop_project.application.dto.customer_dto import CustomerDTO
from shop_project.infrastructure.query.domain_load_query import DomainLoadQuery
from shop_project.infrastructure.repositories.base_repository import BaseRepository
from shop_project.domain.customer import Customer
from shop_project.infrastructure.database.models.customer import Customer as CustomerORM
from shop_project.shared.entity_id import EntityId

class MockRepository(BaseRepository[Any]):
    async def create(self, items: list[Any]) -> None:
        """Создает список Customers одним запросом через bulk_insert."""
        return

    async def update(self, items: list[Any]) -> None:
        """Обновляет список Customers одним запросом через bulk_update."""
        return

    async def delete(self, items: list[Any]) -> None:
        """Удаляет список Customers одним запросом через bulk_delete."""
        return