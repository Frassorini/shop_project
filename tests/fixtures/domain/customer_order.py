from typing import Callable

import pytest

from domain.store import Store
from domain.customer import Customer
from domain.customer_order import CustomerOrder, CustomerOrderState
from shared.entity_id import EntityId


@pytest.fixture
def customer_order_factory(
    unique_id_factory: Callable[[], EntityId],
    customer_andrew: Callable[[], Customer],
    store_factory_with_cache: Callable[[str], Store],
) -> Callable[[], CustomerOrder]:
    def factory() -> CustomerOrder:
        store_obj: Store = store_factory_with_cache('Moscow')
        order = CustomerOrder(entity_id=unique_id_factory(), customer_id=customer_andrew().entity_id, store_id=store_obj.entity_id)
        return order
    return factory


@pytest.fixture
def transition_order_to_state() -> Callable[[CustomerOrder, CustomerOrderState], None]:
    def factory(order: CustomerOrder, state: CustomerOrderState) -> None:
        if order.state != CustomerOrderState.PENDING:
            raise ValueError(f'TEST ERROR: CustomerOrder must be in {CustomerOrderState.PENDING} state')
        
        match state:
            case CustomerOrderState.PENDING:
                pass
            case CustomerOrderState.RESERVED:
                order.reserve()
            case CustomerOrderState.PAID:
                order.reserve()
                order.pay()
            case CustomerOrderState.CLAIMED:
                order.reserve()
                order.pay()
                order.claim()
            case CustomerOrderState.UNCLAIMED:
                order.reserve()
                order.pay()
                order.unclaim()
            case CustomerOrderState.REFUNDED:
                order.reserve()
                order.pay()
                order.claim()
                order.refund()
            case CustomerOrderState.CANCELLED:
                order.reserve()
                order.cancel()
    return factory