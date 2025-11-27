from typing import Any

from shop_project.infrastructure.repositories.base_repository import BaseRepository


class MockRepository(BaseRepository[Any, Any]):
    async def create(self, items: list[Any]) -> None:
        """Создает список Customers одним запросом через bulk_insert."""
        return

    async def update(self, items: list[Any]) -> None:
        """Обновляет список Customers одним запросом через bulk_update."""
        return

    async def delete(self, items: list[Any]) -> None:
        """Удаляет список Customers одним запросом через bulk_delete."""
        return
