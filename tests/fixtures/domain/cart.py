from typing import Callable
import pytest

from domain.cart import Cart
from domain.customer import Customer
from domain.store import Store
from shared.entity_id import EntityId


@pytest.fixture
def cart_factory(unique_id_factory: Callable[[], EntityId],
                 customer_andrew: Callable[[], Customer],
                 store_factory_with_cache: Callable[[str], Store]) -> Callable[[], Cart]:
    def factory() -> Cart:
        store_obj: Store = store_factory_with_cache('Moscow')
        cart = Cart(unique_id_factory(), customer_id=customer_andrew().entity_id, store_id=store_obj.entity_id)
        return cart
    return factory