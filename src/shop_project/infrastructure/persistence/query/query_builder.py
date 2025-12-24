from dataclasses import dataclass
from typing import Any, Self, Type
from uuid import UUID

from shop_project.application.interfaces.interface_query_builder import IQueryBuilder
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.infrastructure.persistence.query.composed_query import QueryLock
from shop_project.infrastructure.persistence.query.custom_query import CustomQuery
from shop_project.infrastructure.persistence.query.query_criteria import QueryCriteria
from shop_project.infrastructure.persistence.query.query_plan import (
    LockQueryPlan,
    NoLockQueryPlan,
    QueryPlan,
)
from shop_project.infrastructure.persistence.query.value_container import ValueContainer
from shop_project.infrastructure.persistence.query.value_extractor import ValueExtractor
from shop_project.infrastructure.registries.load_resolution_registry import (
    DomainReferenceRegistry,
    LoadResolutionDescriptor,
)


@dataclass
class QueryData:
    model_type: type | None
    criteria: QueryCriteria
    lock: QueryLock | None

    @property
    def is_not_empty(self) -> bool:
        return (
            self.model_type is not None
            or self.lock is not None
            or not self.criteria.is_empty
        )


# lock == True  -> Все запросы должны быть FOR UPDATE/FOR SHARE
# lock == False -> Все запросы должны быть без блокирования
class QueryBuilder(IQueryBuilder):
    def __init__(self, mutating: bool) -> None:
        self.domain_reference_registry: Type[DomainReferenceRegistry] = (
            DomainReferenceRegistry
        )
        self.query_plan: QueryPlan
        if mutating:
            self.query_plan = LockQueryPlan()
        else:
            self.query_plan = NoLockQueryPlan()
        self._current_query_data: QueryData = QueryData(None, QueryCriteria(), None)
        self._first_query: bool = True

    def _build_query(self) -> None:
        self.query_plan.add_query(
            self._current_query_data.model_type,
            self._current_query_data.criteria,
            self._current_query_data.lock,
        )

        self._current_query_data = QueryData(None, QueryCriteria(), None)

    def add_prebuilt(self, prebuilt_query: CustomQuery) -> Self:
        self.query_plan.add_prebuilt(prebuilt_query)

        return self

    def load(self, entity_type: Type[PersistableEntity]) -> Self:
        if not self._first_query:
            self._build_query()
        else:
            self._first_query = False

        self._current_query_data = QueryData(entity_type, QueryCriteria(), None)

        return self

    def and_(self) -> Self:
        self._current_query_data.criteria.and_()

        return self

    def or_(self) -> Self:
        self._current_query_data.criteria.or_()

        return self

    def greater_than(self, attribute_name: str, value: Any) -> Self:
        provider = ValueContainer([value])

        self._current_query_data.criteria.criterion_greater_than(
            attribute_name, provider
        )

        return self

    def lesser_than(self, attribute_name: str, value: Any) -> Self:
        provider = ValueContainer([value])

        self._current_query_data.criteria.criterion_lesser_than(
            attribute_name, provider
        )

        return self

    def from_attribute(self, attribute_name: str, attribute_values: list[Any]) -> Self:
        attribute_container: ValueContainer = ValueContainer(attribute_values)

        self._current_query_data.criteria.criterion_in(
            attribute_name, attribute_container
        )

        return self

    def from_id(self, attribute_values: list[UUID]) -> Self:
        return self.from_attribute("entity_id", attribute_values)

    def for_update(self, no_wait: bool = False) -> Self:
        if no_wait:
            self._current_query_data.lock = QueryLock.EXCLUSIVE_NOWAIT
        else:
            self._current_query_data.lock = QueryLock.EXCLUSIVE

        return self

    def for_share(self, no_wait: bool = False) -> Self:
        if no_wait:
            self._current_query_data.lock = QueryLock.SHARED_NOWAIT
        else:
            self._current_query_data.lock = QueryLock.SHARED

        return self

    def no_lock(self) -> Self:
        self._current_query_data.lock = QueryLock.NO_LOCK

        return self

    def from_previous(self, query_index: int | None = None) -> Self:
        if self._current_query_data.model_type is None:
            raise ValueError("No model type found")

        previous_query = self.query_plan.get_previous_query(query_index)

        reference_descriptor: LoadResolutionDescriptor[PersistableEntity] = (
            self.domain_reference_registry.get_reference_descriptor(
                previous_query.model_type, self._current_query_data.model_type
            )
        )

        extractor = ValueExtractor(previous_query, reference_descriptor.strategy)

        self._current_query_data.criteria.criterion_in(
            reference_descriptor.attribute_name, extractor
        )

        return self

    def build(self) -> QueryPlan:
        if self._current_query_data.is_not_empty:
            self._build_query()

        self.query_plan.validate_build()

        return self.query_plan
