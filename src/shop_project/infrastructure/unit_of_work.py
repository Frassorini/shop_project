from typing import Literal, Self
from sqlalchemy.ext.asyncio import AsyncSession
from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.infrastructure.repositories.repository_container import RepositoryContainer, repository_container_factory
from shop_project.infrastructure.resource_manager.resource_container import ResourceContainer
from shop_project.infrastructure.resource_manager.resource_manager import ResourceManager
from shop_project.infrastructure.exceptions import UnitOfWorkException
from shop_project.shared.entity_id import EntityId

from shop_project.infrastructure.registries.repository_registry import RepositoryRegistry
from shop_project.infrastructure.registries.resources_registry import ResourcesRegistry
from shop_project.infrastructure.registries.total_order_registry import TotalOrderRegistry

from shop_project.application.interfaces.interface_query_builder import IQueryBuilder
from shop_project.application.interfaces.interface_unit_of_work import IUnitOfWork, IUnitOfWorkFactory

class UnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession, *, 
                 resource_manager: ResourceManager) -> None:
        self.session: AsyncSession = session
        self.resource_manager: ResourceManager = resource_manager
        self.read_only: bool = resource_manager.read_only
        self._query_plan: QueryBuilder | None = None
        
        self.exhausted = False
    
    def set_query_plan(self, query_plan: IQueryBuilder) -> None:
        if not isinstance(query_plan, QueryBuilder):
            raise NotImplementedError
        self._query_plan = query_plan 
    
    async def __aenter__(self) -> Self:
        if self.exhausted:
            raise UnitOfWorkException('UnitOfWork is exhausted')
        
        if not self.read_only:
            self.session.begin()
        
        if self._query_plan:
            await self.resource_manager.load(self._query_plan.build())
        
        self.resource_manager.resource_container.take_snapshot()
        
        return self
    
    def get_resorces(self) -> ResourceContainer:
        return self.resource_manager.resource_container
    
    def get_unique_id(self, model_type: type[BaseAggregate]) -> EntityId:
        return self.resource_manager.get_unique_id(model_type)
    
    async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Exception | None) -> None:
        if exc_type is not None and not self.exhausted:
            if not self.read_only:
                await self.rollback()

        self.exhausted = True
    
    async def commit(self):
        if self.read_only:
            raise UnitOfWorkException('Cannot commit read only UnitOfWork')
        
        await self.resource_manager.save()
        await self.session.commit()
        self.exhausted = True
    
    async def rollback(self):
        await self.session.rollback()
        self.exhausted = True


class UnitOfWorkFactory(IUnitOfWorkFactory):
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session
    
    def create(self, mode: Literal["read_only", "read_write"]) -> UnitOfWork:
        if not mode in ['read_only', 'read_write']:
            raise ValueError(f'Invalid mode: {mode}')
        
        repository_container = repository_container_factory(session=self.session, repositories=RepositoryRegistry.get_map())
        
        resource_manager = ResourceManager(
            repository_container=repository_container, 
            resources_registry=ResourcesRegistry.get_map(), 
            total_order=TotalOrderRegistry, 
            read_only=mode == 'read_only')
        
        return UnitOfWork(self.session, resource_manager=resource_manager)
