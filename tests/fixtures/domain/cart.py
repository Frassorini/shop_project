from typing import Callable
import pytest

from shop_project.domain.cart import Cart
from shop_project.domain.customer import Customer
from shop_project.domain.store import Store
from shop_project.shared.entity_id import EntityId

from tests.helpers import AggregateContainer


@pytest.fixture
def cart_factory(unique_id_factory: Callable[[], EntityId],
                 customer_andrew: Callable[[], Customer],
                 store_factory_with_cache: Callable[[str], Store]) -> Callable[[], Cart]:
    def factory() -> Cart:
        store_obj: Store = store_factory_with_cache('Moscow')
        cart = Cart(unique_id_factory(), customer_id=customer_andrew().entity_id, store_id=store_obj.entity_id)
        return cart
    return factory



@pytest.fixture
def cart_container_factory(unique_id_factory: Callable[[], EntityId],
                 customer_andrew: Callable[[], Customer],
                 store_factory_with_cache: Callable[[str], Store]) -> Callable[[], AggregateContainer]:
    def factory() -> AggregateContainer:
        store: Store = store_factory_with_cache('Moscow')
        customer = customer_andrew()
        cart = Cart(unique_id_factory(), customer_id=customer.entity_id, store_id=store.entity_id)
        
        container = AggregateContainer(aggregate=cart, dependencies={Customer: [customer], Store: [store]})
        return container
    return factory