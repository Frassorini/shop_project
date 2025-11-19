from typing import Literal

from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.query.base_query import BaseQuery, QueryLock


class CustomQuery(BaseQuery):
    return_type: Literal["DOMAIN", "SCALARS"]

    def __init__(
        self,
        lock: Literal["NO_LOCK", "EXCLUSIVE", "SHARED"],
    ) -> None:
        self.lock: QueryLock = QueryLock(lock)
        self._result: list[PersistableEntity] = []
        self._is_loaded: bool = False

    def load(self, result: list[PersistableEntity]) -> None:
        if self._is_loaded:
            raise RuntimeError("Query is already loaded")

        self._result = result
        self._is_loaded = True

    def get_result(self) -> list[PersistableEntity]:
        if not self._is_loaded:
            raise RuntimeError("Query is not loaded")

        return self._result

    def set_args(self) -> None:
        pass
