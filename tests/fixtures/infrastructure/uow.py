from typing import Any, Callable, Type, TypeVar

import pytest

from shop_project.application.interfaces.p_repository import PRepository
from shop_project.domain.store import Store
from shop_project.p_session import PSession
from shop_project.infrastructure.repositories.repository_container import RepositoryContainer
from shop_project.infrastructure.resource_manager.resource_manager import ResourceManager
from shop_project.domain.cart import Cart
from shop_project.domain.customer import Customer
from shop_project.domain.customer_order import CustomerOrder
from shop_project.unit_of_work import UnitOfWork
from shop_project.domain.store_item import StoreItem
from shop_project.domain.supplier_order import SupplierOrder


DomainObject = TypeVar('DomainObject')


@pytest.fixture
def fake_repository_container_factory(
    fake_repository: Callable[[Type[Any], list[Any]], PRepository[Any]],
    ) -> Callable[[PSession, dict[Type[Any], list[Any]]], RepositoryContainer]:
    def factory(session: PSession, items_by_type: dict[Type[Any], list[Any]]) -> RepositoryContainer:
        type_arg_map: dict[Type[Any], PRepository[Any]] = {
            Customer: fake_repository(Customer, []),
            CustomerOrder: fake_repository(CustomerOrder, []),
            SupplierOrder: fake_repository(SupplierOrder, []),
            Cart: fake_repository(Cart, []),
            StoreItem: fake_repository(StoreItem, []),
            Store: fake_repository(Store, []),
        } 
        
        for repository_type, items in items_by_type.items():
            type_arg_map[repository_type] = fake_repository(repository_type, items)
        
        return RepositoryContainer(session, type_arg_map)
    
    return factory


@pytest.fixture
def fake_uow_factory(fake_repository_container_factory: Callable[[PSession, dict[Type[Any], list[Any]]], RepositoryContainer],
                     fake_session_factory: Callable[[], PSession]) -> Callable[[dict[Type[Any], list[Any]], str], UnitOfWork]:
    def factory(items_by_type: dict[Type[Any], list[Any]], policy: str) -> UnitOfWork:
        session: PSession = fake_session_factory()
        repository_container: RepositoryContainer = fake_repository_container_factory(session, items_by_type)
        
        if policy == 'read_only':
            read_only_flag = True
        elif policy == 'read_write':
            read_only_flag = False
        else:
            raise ValueError(f'Unknown policy value {policy}')
        
        return UnitOfWork(session, repository_container, read_only=read_only_flag)
    
    return factory


@pytest.fixture
def rebuild_fake_repository_container() -> Callable[[PSession, RepositoryContainer], RepositoryContainer]:
    def factory(session: PSession, repository_container: RepositoryContainer) -> RepositoryContainer:
        type_arg_map: dict[Type[Any], PRepository[Any]] = {}
        
        for repository_type, repository in repository_container.repositories.items():
            type_arg_map[repository_type] = repository.clone() # type: ignore
        
        return RepositoryContainer(session, type_arg_map)
    
    return factory


@pytest.fixture
def rebuild_fake_uow(fake_session_factory: Callable[[], PSession],
                     rebuild_fake_repository_container: Callable[[PSession, RepositoryContainer], RepositoryContainer]
                     ) -> Callable[[UnitOfWork, str], UnitOfWork]:
    def factory(uow: UnitOfWork, policy: str) -> UnitOfWork:
        session: PSession = fake_session_factory()
        
        repository_container: RepositoryContainer = rebuild_fake_repository_container(session, uow.resource_manager.repository_container)
        
        if policy == 'read_only':
            read_only_flag = True
        elif policy == 'read_write':
            read_only_flag = False
        else:
            raise ValueError(f'Unknown policy value {policy}')
        
        return UnitOfWork(session, repository_container, read_only=read_only_flag)
    
    return factory
