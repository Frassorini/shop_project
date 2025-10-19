from typing import Callable

import pytest

from shop_project.domain.store import Store
from shop_project.domain.customer import Customer
from shop_project.domain.purchase_active import PurchaseActive, PurchaseActiveState
from shop_project.domain.store_item import StoreItem
from shop_project.shared.entity_id import EntityId

from tests.helpers import AggregateContainer


@pytest.fixture
def customer_order_factory(
    unique_id_factory: Callable[[], EntityId],
    customer_andrew: Callable[[], Customer],
    store_factory_with_cache: Callable[[str], Store],
) -> Callable[[], PurchaseActive]:
    def factory() -> PurchaseActive:
        store_obj: Store = store_factory_with_cache('Moscow')
        order = PurchaseActive(entity_id=unique_id_factory(), customer_id=customer_andrew().entity_id, store_id=store_obj.entity_id)
        return order
    return factory


@pytest.fixture
def customer_order_container_factory(
    unique_id_factory: Callable[[], EntityId],
    customer_andrew: Callable[[], Customer],
    store_factory_with_cache: Callable[[str], Store],
    store_item_container_factory: Callable[..., AggregateContainer],
) -> Callable[[], AggregateContainer]:
    def factory() -> AggregateContainer:
        store: Store = store_factory_with_cache('Moscow')
        customer = customer_andrew()
        order = PurchaseActive(entity_id=unique_id_factory(), customer_id=customer.entity_id, store_id=store.entity_id)
        store_item = store_item_container_factory(name='potatoes', amount=1, store=store, price=1).aggregate
        
        container: AggregateContainer = AggregateContainer(
            aggregate=order, 
            dependencies={Customer: [customer], 
                          StoreItem: [store_item], 
                          Store: [store]})
        
        return container
    return factory


@pytest.fixture
def transition_order_to_state() -> Callable[[PurchaseActive, PurchaseActiveState], None]:
    def factory(order: PurchaseActive, state: PurchaseActiveState) -> None:
        if order.state != PurchaseActiveState.PENDING:
            raise ValueError(f'TEST ERROR: PurchaseActive must be in {PurchaseActiveState.PENDING} state')
        
        match state:
            case PurchaseActiveState.PENDING:
                pass
            case PurchaseActiveState.RESERVED:
                order.reserve()
            case PurchaseActiveState.PAID:
                order.reserve()
                order.pay()
            case PurchaseActiveState.CLAIMED:
                order.reserve()
                order.pay()
                order.claim()
            case PurchaseActiveState.UNCLAIMED:
                order.reserve()
                order.pay()
                order.unclaim()
            case PurchaseActiveState.REFUNDED:
                order.reserve()
                order.pay()
                order.claim()
                order.refund()
            case PurchaseActiveState.CANCELLED:
                order.reserve()
                order.cancel()
    return factory