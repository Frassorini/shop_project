from abc import ABC, abstractmethod
from typing import Any, Literal, Type, TypeVar

from shop_project.application.dto.base_dto import BaseDTO
from shop_project.application.interfaces.interface_query_plan import IQueryPlan
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.exceptions import QueryPlanException
from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery, QueryLock
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.query.query_criteria import QueryCriteria
from shop_project.infrastructure.registries.total_order_registry import (
    TotalOrderRegistry,
)

T = TypeVar("T")


def _ensure_not_none(value: T | None, fail_message: str) -> T:
    if value is None:
        raise QueryPlanException(f"{fail_message}")
    return value


class QueryPlan(ABC, IQueryPlan):
    read_only: bool
    queries: list[BaseQuery]

    @abstractmethod
    def _validate_query(self, query: BaseQuery) -> None: ...

    def add_query(
        self,
        model_type: Type[PersistableEntity] | None,
        criteria: QueryCriteria | None,
        lock: QueryLock | None,
    ) -> None:

        model_type = _ensure_not_none(model_type, "model type not specified")
        criteria = _ensure_not_none(criteria, "criteria not specified")
        lock = _ensure_not_none(lock, "lock not specified")

        query = ComposedQuery(model_type, criteria, lock)

        self._validate_query(query)

        self.queries.append(query)

    def add_prebuilt(self, prebuilt_query: CustomQuery) -> None:
        self.queries.append(prebuilt_query)

    def get_previous_query(self, query_index: int | None = None) -> BaseQuery:
        if query_index is None:
            query_index = len(self.queries) - 1

        if query_index < 0 or query_index >= len(self.queries):
            raise ValueError("Invalid query index")

        return self.queries[query_index]

    @abstractmethod
    def validate_build(self) -> None: ...

    @abstractmethod
    def validate_changes(
        self,
        resource_changes_snapshot: dict[
            Type[PersistableEntity],
            dict[Literal["CREATED", "UPDATED", "DELETED"], list[BaseDTO[Any]]],
        ],
    ) -> None: ...


class NoLockQueryPlan(QueryPlan):
    read_only = True

    def __init__(self) -> None:
        self.queries: list[BaseQuery] = []

    def _validate_query(self, query: BaseQuery) -> None:
        if not query.lock == QueryLock.NO_LOCK:
            raise QueryPlanException(
                "Only no lock queries are allowed in no lock query plan"
            )

    def validate_build(self):
        pass

    def validate_changes(
        self,
        resource_changes_snapshot: dict[
            Type[PersistableEntity],
            dict[Literal["CREATED", "UPDATED", "DELETED"], list[BaseDTO[Any]]],
        ],
    ) -> None:
        for model_type, model_changes in resource_changes_snapshot.items():
            is_changed = (
                model_changes["CREATED"]
                or model_changes["UPDATED"]
                or model_changes["DELETED"]
            )

            if is_changed:
                raise QueryPlanException(
                    f"Model type {model_type} is changed in no lock query plan"
                )


class LockQueryPlan(QueryPlan):
    read_only = False

    def __init__(self) -> None:
        self.queries: list[BaseQuery] = []

    def _validate_query(self, query: BaseQuery) -> None:
        if not query.lock == QueryLock.EXCLUSIVE and not query.lock == QueryLock.SHARED:
            raise QueryPlanException(
                "Only locking queries are allowed in locking query plan"
            )

    def _build_map(self) -> dict[Type[Any], BaseQuery]:
        result: dict[Type[Any], BaseQuery] = {}

        for query in self.queries:
            result[query.model_type] = query

        return result

    def _validate_single_query_per_model_type(self) -> None:
        for query in self.queries:
            model_type = query.model_type

            model_type_count = sum(
                1 for q in self.queries if q.model_type == model_type
            )

            if model_type_count > 1:
                raise QueryPlanException(
                    f"Multiple queries for model type {model_type} in locking query plan"
                )

    def validate_build(self) -> None:

        self._validate_single_query_per_model_type()

        for previous_query, current_query in zip(self.queries, self.queries[1:]):
            previous_priority = TotalOrderRegistry.get_priority(
                previous_query.model_type
            )
            current_priority = TotalOrderRegistry.get_priority(current_query.model_type)

            if previous_priority >= current_priority:
                raise QueryPlanException("locking order violation")

    def validate_changes(
        self,
        resource_changes_snapshot: dict[
            Type[PersistableEntity],
            dict[Literal["CREATED", "UPDATED", "DELETED"], list[BaseDTO[Any]]],
        ],
    ) -> None:
        query_map = self._build_map()

        for model_type, model_changes in resource_changes_snapshot.items():
            query = query_map.get(model_type)

            has_created = True if model_changes["CREATED"] else False
            has_updated = True if model_changes["UPDATED"] else False
            has_deleted = True if model_changes["DELETED"] else False

            # Разрешаем все create даже без соответствующего запроса
            if has_created:
                pass

            if has_updated or has_deleted:
                if query is None:
                    raise QueryPlanException(
                        f"Model type {model_type} is changed without query"
                    )
                if query.lock == QueryLock.SHARED:
                    raise QueryPlanException(
                        f"Model type {model_type} is locked in FOR SHARE mode"
                    )
            else:
                if query is not None and query.lock == QueryLock.EXCLUSIVE:
                    # TODO: log.warning in test/dev environment
                    pass
