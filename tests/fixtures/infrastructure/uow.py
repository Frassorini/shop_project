from typing import Type

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.infrastructure.unit_of_work import UnitOfWork
from shop_project.infrastructure.repositories.repository_container import RepositoryContainer, repository_container_factory


@pytest.fixture
def uow_factory():
    def factory(session: AsyncSession, policy: str) -> UnitOfWork:
        repository_container: RepositoryContainer = repository_container_factory(session)
        
        if policy == 'read_only':
            read_only_flag = True
        elif policy == 'read_write':
            read_only_flag = False
        else:
            raise ValueError(f'Unknown policy value {policy}')
        
        return UnitOfWork(session, repository_container, read_only=read_only_flag)
    
    return factory