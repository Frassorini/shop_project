from typing import Callable
from application.interfaces.id_container import IdContainer
from application.interfaces.id_extractor import IdExtractor
from application.interfaces.load_query import LoadQuery
from domain.customer_order.model import CustomerOrder
from domain.store_item.model import StoreItem
from shared.entity_id import EntityId
from application.interfaces.resource_container import ResourceContainer


def test_query(customer_order_factory: Callable[[], CustomerOrder],
               potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    ids_customer_order: IdContainer = IdContainer([EntityId(1)])
    query_customer_order: LoadQuery[CustomerOrder] = LoadQuery[CustomerOrder](CustomerOrder, ids_customer_order)
    
    def customer_order_to_store_item_ids(customer_order: CustomerOrder) -> list[EntityId]:
        return [item.store_item_id for item in customer_order.get_items()]
    
    ids_store_item: IdExtractor[CustomerOrder] = IdExtractor[CustomerOrder](query_customer_order, customer_order_to_store_item_ids)
    query_store_item: LoadQuery[StoreItem] = LoadQuery[StoreItem](StoreItem, ids_store_item)
    
    customer_order: CustomerOrder = customer_order_factory()
    store_item: StoreItem = potatoes_store_item_10()
    
    customer_order.add_item(store_item_id=store_item.entity_id, price=store_item.price, amount=2, store=store_item.store)
    
    resource_container: ResourceContainer = ResourceContainer()
    resource_container.repository_container.repositories[CustomerOrder].fill([customer_order])
    resource_container.repository_container.repositories[StoreItem].fill([store_item])
    
    resource_container.load([query_customer_order, query_store_item])
    
    assert query_customer_order.is_loaded
    
    assert resource_container.get_by_id(StoreItem, store_item.entity_id) == store_item
    assert resource_container.get_by_id(CustomerOrder, customer_order.entity_id) == customer_order
    
    # query_store_item.result = query_store_item.id_provider.extract()