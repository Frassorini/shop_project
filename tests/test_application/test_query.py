from typing import Callable
from application.resource_loader.attribute_container import AttributeContainer
from application.resource_loader.attribute_extractor import AttributeExtractor
from application.resource_loader.load_query import LoadQuery
from domain.customer_order.model import CustomerOrder
from domain.store_item.model import StoreItem
from shared.entity_id import EntityId
from application.resource_loader.resource_loader import ResourceContainer, ResourceManager, RepositoryContainer
from application.interfaces.p_repository import PRepository


def test_query(customer_order_factory: Callable[[], CustomerOrder],
               potatoes_store_item_10: Callable[[], StoreItem],
               mock_store_item_repository: Callable[[list[StoreItem]], PRepository[StoreItem]],
               mock_customer_order_repository: Callable[[list[CustomerOrder]], PRepository[CustomerOrder]],) -> None:
    ids_customer_order: AttributeContainer[EntityId] = AttributeContainer[EntityId]('entity_id', [EntityId(1)])
    query_customer_order: LoadQuery[CustomerOrder, EntityId] = LoadQuery[CustomerOrder, EntityId](CustomerOrder, ids_customer_order)
    
    def customer_order_to_store_item_ids(customer_order: CustomerOrder) -> list[EntityId]:
        return [item.store_item_id for item in customer_order.get_items()]
    
    ids_store_item: AttributeExtractor[CustomerOrder, EntityId] = \
        AttributeExtractor[CustomerOrder, EntityId](query_customer_order, 'entity_id', customer_order_to_store_item_ids)
    query_store_item: LoadQuery[StoreItem, EntityId] = LoadQuery[StoreItem, EntityId](StoreItem, ids_store_item)
    
    customer_order: CustomerOrder = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    customer_order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store=store_item.store)
    
    resource_loader: ResourceManager = ResourceManager(
        RepositoryContainer(
            customer_order=mock_customer_order_repository([customer_order]),
            store_item=mock_store_item_repository([store_item]),
            ))
    resource_loader.repository_container.repositories[CustomerOrder].fill([customer_order])
    resource_loader.repository_container.repositories[StoreItem].fill([store_item])
    
    resource_container: ResourceContainer = resource_loader.load([query_customer_order, query_store_item])
    
    assert query_customer_order.is_loaded
    
    assert resource_container.get_by_id(StoreItem, store_item.entity_id) == store_item
    assert resource_container.get_by_id(CustomerOrder, customer_order.entity_id) == customer_order
    
    # query_store_item.result = query_store_item.id_provider.extract()