from typing import Any, Callable, Type, TypeVar

import pytest
from application.interfaces.p_repository import PRepository
from application.resource_loader.attribute_container import AttributeContainer
from application.resource_loader.attribute_extractor import AttributeExtractor
from application.resource_loader.query_plan import QueryPlan
from application.resource_loader.load_query import LoadQuery
from domain.customer_order import CustomerOrder
from domain.store_item import StoreItem
from shared.entity_id import EntityId

from application.resource_loader.resource_manager import ResourceManager
from application.resource_loader.resource_container import ResourceContainer
from application.resource_loader.repository_container import RepositoryContainer
from tests.fixtures.fake_repository import FakeRepository


DomainObject = TypeVar('DomainObject')


@pytest.mark.parametrize('model_type', [CustomerOrder, StoreItem],)
def test_create(model_type: Type[DomainObject], 
          domain_object_factory: Callable[[Type[DomainObject]], DomainObject],
          fake_repository_container_factory: Callable[[dict[Type[Any], list[Any]]], RepositoryContainer]) -> None:
    domain_object: DomainObject = domain_object_factory(model_type)
    resource_manager: ResourceManager = ResourceManager(
        fake_repository_container_factory({
            model_type: [domain_object],
            }))
    
    
    
    