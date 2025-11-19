from shop_project.infrastructure.query.query_plan import QueryPlan


from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncIterator, Callable, Literal, Self
from sqlalchemy.ext.asyncio import AsyncSession
from shop_project.domain.persistable_entity import PersistableEntity
from shop_project.infrastructure.database.core import Database
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
    def __init__(self, resource_manager: ResourceManager) -> None:
        self.resource_manager: ResourceManager = resource_manager
        self._commit_requested: bool = False

    def get_resorces(self) -> ResourceContainer:
        return self.resource_manager.resource_container
    
    def get_unique_id(self, model_type: type[PersistableEntity]) -> EntityId:
        return self.resource_manager.get_unique_id(model_type)
    
    def mark_commit(self) -> None:
        self._commit_requested = True
    
    @property
    def commit_requested(self) -> bool:
        return self._commit_requested


class UnitOfWorkFactory(IUnitOfWorkFactory):
    def __init__(self, database: Database) -> None:
        self.database: Database = database
    
    @asynccontextmanager
    async def create(self, query_plan_builder: IQueryBuilder | None = None) -> AsyncIterator[UnitOfWork]:
        if query_plan_builder is None:
            query_plan_builder = QueryBuilder(mutating=False)
        if not isinstance(query_plan_builder, QueryBuilder):
            raise NotImplementedError
        query_plan: QueryPlan = query_plan_builder.build()

        async with self.database.session() as session:
            try:
                repository_container = repository_container_factory(session=session, repositories=RepositoryRegistry.get_map())

                resource_manager = ResourceManager(
                    repository_container=repository_container, 
                    resources_registry=ResourcesRegistry.get_map(), 
                    total_order=TotalOrderRegistry, 
                    read_only=query_plan.read_only)

                await resource_manager.load(query_plan)
                resource_manager.resource_container.take_snapshot()
                
                unit_of_work = UnitOfWork(resource_manager=resource_manager)

                yield unit_of_work
                
                if unit_of_work.commit_requested:
                    if not query_plan.read_only:
                        await resource_manager.save()
                        await session.commit()
                    else:
                        raise UnitOfWorkException("Cannot commit in non-mutating mode")
            except Exception as e:
                await session.rollback()
                raise
            
        
