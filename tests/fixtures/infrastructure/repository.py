from typing import Callable, Coroutine

import pytest

from shop_project.domain.entities.customer import Customer
from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.database.models.customer import Customer as CustomerORM
from shop_project.infrastructure.repositories.base_repository import BaseRepository
from shop_project.infrastructure.repositories.customer_repository import CustomerRepository


@pytest.fixture
def inmem_customer_repository_factory(test_db_in_memory: Database) -> Callable[[list[Customer]], Coroutine[None, None, BaseRepository[Customer]]]:
    async def factory(customers: list[Customer]) -> BaseRepository[Customer]:
        session = test_db_in_memory.create_session()
        repository = CustomerRepository(session)
        await repository.create(customers)
        return repository

    return factory