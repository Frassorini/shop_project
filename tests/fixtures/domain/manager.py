from typing import Callable
from uuid import UUID

import pytest

from shop_project.domain.entities.manager import Manager


@pytest.fixture
def manager_tom(
    unique_id_factory: Callable[[], UUID],
) -> Callable[[], Manager]:
    return lambda: Manager(unique_id_factory(), name="tom")
