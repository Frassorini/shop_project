from typing import Callable

import pytest

from shop_project.domain.store import Store
from shop_project.shared.entity_id import EntityId


@pytest.fixture
def store_factory(unique_id_factory: Callable[[], EntityId]) -> Callable[[str], Store]:
    
    def fact(name: str) -> Store:
        return Store(unique_id_factory(), name=name)
    
    return fact


@pytest.fixture
def store_factory_with_cache(unique_id_factory: Callable[[], EntityId]) -> Callable[[str], Store]:
    cache: dict[str, Store] = {}

    def factory(name: str) -> Store:
        if name in cache:
            return cache[name]
        
        store = Store(unique_id_factory(), name=name)
        cache[name] = store
        return store
    
    return factory
