from application.interfaces.interfaces import PUnitOfWork
from infrastructure.query.query_builder import QueryPlanBuilder
from infrastructure.repositories.repository_container import RepositoryContainer
from infrastructure.resource_manager.resource_container import ResourceContainer
from infrastructure.resource_manager.resource_manager import ResourceManager
from infrastructure.exceptions import UnitOfWorkException
from infrastructure.p_session import PSession


class UnitOfWork(PUnitOfWork):
    def __init__(self, session: PSession, repository_container: RepositoryContainer, *, read_only: bool) -> None:
        self.session: PSession = session
        self.read_only = read_only
        self.resource_manager: ResourceManager = ResourceManager(repository_container, read_only=read_only)
        self._query_plan: QueryPlanBuilder | None = None
        
        self.exhausted = False
    
    def set_query_plan(self, query_plan: QueryPlanBuilder) -> None:
        self._query_plan = query_plan
    
    def __enter__(self):
        if self.exhausted:
            raise UnitOfWorkException('UnitOfWork is exhausted')
        
        if not self.read_only:
            self.session.begin()
        
        if self._query_plan:
            self.resource_manager.load(self._query_plan.build())
        
        self.resource_manager.resource_container.take_snapshot()
        
        return self
    
    def get_resorces(self) -> ResourceContainer:
        return self.resource_manager.resource_container
    
    def __exit__(self, exc_type: type | None, exc_val, exc_tb):
        if exc_type is not None and not self.exhausted:
            self.rollback()
        
        self.exhausted = True
    
    def commit(self):
        if self.read_only:
            raise UnitOfWorkException('Cannot commit read only UnitOfWork')
        
        self.resource_manager.save()
        self.session.commit()
        self.exhausted = True
    
    def rollback(self):
        self.session.rollback()
        self.exhausted = True


