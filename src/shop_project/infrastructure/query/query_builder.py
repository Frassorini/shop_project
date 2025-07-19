from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, Self, Type, TypeVar

from shop_project.domain.p_aggregate import PAggregate
from shop_project.exceptions import QueryPlanException
from shop_project.infrastructure.query.value_extractor import ValueExtractor
from shop_project.infrastructure.query.query_criteria import QueryCriteria, QueryCriterion
from shop_project.infrastructure.resource_manager.domain_reference_registry import DomainReferenceDescriptor, DomainReferenceRegistry
from shop_project.infrastructure.resource_manager.lock_total_order_registry import LockTotalOrderRegistry

from shop_project.infrastructure.query.value_container import ValueContainer
from shop_project.infrastructure.query.load_query import LoadQuery, QueryLock
from shop_project.infrastructure.query.p_value_provider import PValueProvider
from shop_project.infrastructure.query.query_plan import LockQueryPlan, NoLockQueryPlan, QueryPlan


@dataclass
class QueryData:
    model_type: type | None
    criteria: QueryCriteria
    lock: QueryLock | None


# lock == True  -> Все запросы должны быть FOR UPDATE/FOR SHARE
# lock == False -> Все запросы должны быть без блокирования
class QueryPlanBuilder:
    def __init__(self, mutating: bool) -> None:
        self.domain_reference_registry: Type[DomainReferenceRegistry] = DomainReferenceRegistry
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
            self._current_query_data.lock
            )
        
        self._current_query_data = QueryData(None, QueryCriteria(), None)
    
    def load(self, entity_type: Type[PAggregate]) -> Self:
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
    
    def is_in(self, attribute_name: str, value: str) -> Self:
        provider = ValueContainer([value])
        
        self._current_query_data.criteria.criterion_in(attribute_name, provider)
        
        return self
    
    def equals(self, attribute_name: str, value: str) -> Self:
        provider = ValueContainer([value])
        
        self._current_query_data.criteria.criterion_equals(attribute_name, provider)
        
        return self
    
    def from_attribute(self, attribute_name: str, attribute_values: list[str]) -> Self:
        attribute_container: ValueContainer = ValueContainer(attribute_values)
        
        self._current_query_data.criteria.criterion_in(attribute_name, attribute_container)
        
        return self
    
    def from_id(self, attribute_values: list[str]) -> Self:
        return self.from_attribute("entity_id", attribute_values)
    
    def for_update(self) -> Self:
        self._current_query_data.lock = QueryLock.FOR_UPDATE
        
        return self
    
    def for_share(self) -> Self:
        self._current_query_data.lock = QueryLock.FOR_SHARE
        
        return self
    
    def no_lock(self) -> Self:
        self._current_query_data.lock = QueryLock.NO_LOCK
        
        return self
    
    def from_previous(self, query_index: int | None = None) -> Self:
        if self._current_query_data.model_type is None:
            raise ValueError("No model type found")
        
        previous_query = self.query_plan.get_previous_query(query_index)
        
        reference_descriptor: DomainReferenceDescriptor[PAggregate] = (
            self.domain_reference_registry.get_reference_descriptor(
                previous_query.model_type, self._current_query_data.model_type
                )
            )
        
        extractor = ValueExtractor(previous_query, reference_descriptor.strategy)
        
        self._current_query_data.criteria.criterion_in(reference_descriptor.attribute_name, extractor)
        
        return self

    
    def build(self) -> QueryPlan:
        self._build_query()
        
        self.query_plan.validate_build()
        
        return self.query_plan