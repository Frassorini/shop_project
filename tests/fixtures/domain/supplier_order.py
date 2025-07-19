from datetime import datetime, timezone
from typing import Callable

import pytest

from shop_project.domain.store import Store
from shop_project.shared.entity_id import EntityId
from shop_project.domain.supplier_order import SupplierOrder


@pytest.fixture
def supplier_order_factory(
    unique_id_factory: Callable[[], EntityId],
    store_factory_with_cache: Callable[[str], Store],
) -> Callable[[], SupplierOrder]:
    def factory() -> SupplierOrder:
        store_obj: Store = store_factory_with_cache('Moscow')
        order = SupplierOrder(entity_id=unique_id_factory(), 
                              departure=datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc),
                              arrival=datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc), 
                              store_id=store_obj.entity_id)
        return order
    return factory