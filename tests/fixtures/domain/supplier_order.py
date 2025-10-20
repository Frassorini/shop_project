from datetime import datetime, timezone
from typing import Callable

import pytest

from shop_project.domain.store_item import StoreItem
from shop_project.shared.entity_id import EntityId
from shop_project.domain.supplier_order import SupplierOrder
from tests.helpers import AggregateContainer


@pytest.fixture
def supplier_order_factory(
    unique_id_factory: Callable[[], EntityId],
) -> Callable[[], SupplierOrder]:
    def factory() -> SupplierOrder:
        order = SupplierOrder(entity_id=unique_id_factory(), 
                              departure=datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc),
                              arrival=datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc))
        return order
    return factory


@pytest.fixture
def supplier_order_container_factory(
    unique_id_factory: Callable[[], EntityId],
    store_item_container_factory: Callable[..., AggregateContainer],
) -> Callable[[], AggregateContainer]:
    def factory() -> AggregateContainer:
        order = SupplierOrder(entity_id=unique_id_factory(), 
                              departure=datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc),
                              arrival=datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc))
        
        store_item = store_item_container_factory(name='potatoes', amount=1, price=1).aggregate
        
        container: AggregateContainer = AggregateContainer(
            aggregate=order, 
            dependencies={StoreItem: [store_item]})
        return container

    return factory