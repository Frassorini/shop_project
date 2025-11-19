from typing import Callable
from uuid import uuid4

import pytest

from shop_project.shared.entity_id import EntityId


@pytest.fixture
def unique_id_factory() -> Callable[[], EntityId]:

    def fact() -> EntityId:
        return EntityId(uuid4())

    return fact
