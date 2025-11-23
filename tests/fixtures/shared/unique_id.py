from typing import Callable
from uuid import UUID, uuid4

import pytest


@pytest.fixture
def unique_id_factory() -> Callable[[], UUID]:

    def fact() -> UUID:
        return uuid4()

    return fact
