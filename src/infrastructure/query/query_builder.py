from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal, Self, Type, TypeVar

from domain.p_aggregate import PAggregate
from infrastructure.exceptions import QueryPlanException
from infrastructure.query.attribute_extractor import AttributeExtractor
from infrastructure.resource_manager.domain_reference_registry import DomainReferenceDescriptor, DomainReferenceRegistry
from infrastructure.resource_manager.lock_total_order_registry import LockTotalOrderRegistry

from infrastructure.query.attribute_container import AttributeContainer
from infrastructure.query.load_query import LoadQuery, QueryLock
from infrastructure.query.p_attribute_provider import PAttributeProvider
from infrastructure.query.query_plan import LockingQueryPlan, NoLockQueryPlan, QueryPlan


@dataclass
class QueryData:
    model_type: type | None
    attribute_provider: PAttributeProvider | None
    lock: QueryLock | None


# lock == True  -> Все запросы должны быть FOR UPDATE/FOR SHARE
# lock == False -> Все запросы должны быть без блокирования
class QueryPlanBuilder:
    def __init__(self, mutating: bool) -> None:
        self.domain_reference_registry: Type[DomainReferenceRegistry] = DomainReferenceRegistry
        self.query_plan: QueryPlan
        if mutating:
            self.query_plan = LockingQueryPlan()
        else:
            self.query_plan = NoLockQueryPlan()
        self._current_query_data: QueryData = QueryData(None, None, None)
        self._first_query: bool = True
        
    def _build_query(self) -> None:
        self.query_plan.add_query(
            self._current_query_data.model_type,
            self._current_query_data.attribute_provider,
            self._current_query_data.lock
            )
        
        self._current_query_data = QueryData(None, None, None)
    
    def load(self, entity_type: type[Any]) -> Self:
        if not self._first_query:
            self._build_query()
        else:
            self._first_query = False
        
        self._current_query_data = QueryData(entity_type, None, None)
        
        return self
    
    def from_attribute(self, attribute_name: str, attribute_values: list[Any]) -> Self:
        attribute_container: AttributeContainer = AttributeContainer(attribute_name, attribute_values)
        
        self._current_query_data.attribute_provider = attribute_container
        
        return self
    
    def from_id(self, attribute_values: list[Any]) -> Self:
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
        
        reference_descriptor: DomainReferenceDescriptor[Any] = (
            self.domain_reference_registry.get_reference_descriptor(
                previous_query.model_type, self._current_query_data.model_type
                )
            )
        
        extractor = AttributeExtractor(previous_query, reference_descriptor.attribute_name, reference_descriptor.strategy)
        
        self._current_query_data.attribute_provider = extractor
        
        return self

    
    def build(self) -> QueryPlan:
        self._build_query()
        
        self.query_plan.validate_build()
        
        return self.query_plan