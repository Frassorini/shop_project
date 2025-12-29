from typing import Type

from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.persistence.query.base_query import (
    BaseQuery,
    QueryLock,
)
from shop_project.infrastructure.persistence.query.query_criteria import QueryCriteria


class ComposedQuery(BaseQuery):
    def __init__(
        self,
        model_type: Type[PersistableEntity],
        criteria: QueryCriteria,
        lock: QueryLock,
        order_by: str | None = None,
        order_by_desc: bool = False,
        limit: int | None = None,
    ) -> None:
        self.model_type: Type[PersistableEntity] = model_type
        self.criteria: QueryCriteria = criteria
        self.lock: QueryLock = lock
        self.order_by: str | None = order_by
        self.order_by_desc: bool = order_by_desc
        self.limit: int | None = limit

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
