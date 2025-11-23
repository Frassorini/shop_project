from typing import Callable
from uuid import UUID

import pytest

from shop_project.domain.entities.employee import Employee


@pytest.fixture
def employee_bob(
    unique_id_factory: Callable[[], UUID],
) -> Callable[[], Employee]:
    return lambda: Employee(unique_id_factory(), name="bob")
