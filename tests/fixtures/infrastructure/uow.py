from typing import Literal, Type

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.infrastructure.unit_of_work import UnitOfWork
from shop_project.infrastructure.repositories.repository_container import RepositoryContainer, repository_container_factory


@pytest.fixture
def uow_factory():
    def factory(session: AsyncSession, mode: Literal["read_only", "read_write"]) -> UnitOfWork:
        repository_container: RepositoryContainer = repository_container_factory(session)
 
        return UnitOfWork(session, repository_container, mode=mode)
    
    return factory