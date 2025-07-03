from itertools import count
from typing import Callable
import pytest

from shared.entity_id import EntityId


@pytest.fixture
def unique_id_factory() -> Callable[[], EntityId]:
    
    counter = count(start=1)
    
    def fact() -> EntityId:
        return EntityId(str(next(counter)))
    
    return fact