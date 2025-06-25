from typing import Any, Callable, Type, TypeVar
from infrastructure.query.attribute_container import AttributeContainer
from infrastructure.query.attribute_extractor import AttributeExtractor
from infrastructure.query.load_query import LoadQuery
from domain.customer_order import CustomerOrder
from domain.store_item import StoreItem
from shared.entity_id import EntityId
from infrastructure.resource_manager.resource_manager import ResourceContainer, ResourceManager, RepositoryContainer
from application.interfaces.p_repository import PRepository


DomainObject = TypeVar('DomainObject')
    
    
def test_query(customer_order_factory: Callable[[], CustomerOrder],
               potatoes_store_item_10: Callable[[], StoreItem],
               fake_repository: Callable[[Type[DomainObject], list[DomainObject]], PRepository[DomainObject]],
               fake_session_factory: Callable[[], Any]) -> None:
    ids_customer_order: AttributeContainer = AttributeContainer('entity_id', [EntityId('1')])
    query_customer_order: LoadQuery = LoadQuery(CustomerOrder, ids_customer_order)
    
    def customer_order_to_store_item_ids(customer_order: CustomerOrder) -> list[EntityId]:
        return [item.store_item_id for item in customer_order.get_items()]
    
    ids_store_item: AttributeExtractor = \
        AttributeExtractor(query_customer_order, 'entity_id', customer_order_to_store_item_ids)
    query_store_item: LoadQuery = LoadQuery(StoreItem, ids_store_item)
    
    customer_order: CustomerOrder = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    customer_order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store=store_item.store)
    
    repository_map: dict[Type[Any], PRepository[Any]] = {
        CustomerOrder: fake_repository(CustomerOrder, [customer_order]), # type: ignore
        StoreItem: fake_repository(StoreItem, [store_item]), # type: ignore
    }
    
    resource_loader: ResourceManager = ResourceManager(
        RepositoryContainer(fake_session_factory(), repository_map))
    resource_loader.repository_container.repositories[CustomerOrder].fill([customer_order])
    resource_loader.repository_container.repositories[StoreItem].fill([store_item])
    
    resource_container: ResourceContainer = resource_loader.load([query_customer_order, query_store_item])
    
    assert query_customer_order.is_loaded
    
    assert resource_container.get_by_id(CustomerOrder, customer_order.entity_id) == customer_order
    assert resource_container.get_by_id(StoreItem, store_item.entity_id) == store_item
    
    # query_store_item.result = query_store_item.id_provider.extract()