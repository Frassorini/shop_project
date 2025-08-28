from itertools import count
from pyexpat import model
from typing import Any, Callable, Literal, Type, TypeVar

import pytest
from shop_project.application.dto.base_dto import BaseDTO
from shop_project.application.dto.mapper import to_domain, to_dto
from shop_project.application.interfaces.p_repository import PRepository
from shop_project.domain.base_aggregate import BaseAggregate
import copy

from shop_project.infrastructure.query.load_query import LoadQuery
from shop_project.infrastructure.query.query_criteria import QueryCriteriaOperator, QueryCriterion, QueryCriteria, QueryCriterionOperator
from shop_project.shared.entity_id import EntityId


T = TypeVar('T', bound=BaseAggregate)


class FakeRepository(PRepository[T]):    
    def __init__(self, model_type: Type[T], items: list[T]) -> None:
        self.model_type: Type[T] = model_type
        self._items: dict[EntityId, BaseDTO] = {}
        self.fill(items)
        self._id_counter = count(start=1)
    
    @classmethod
    def from_dict(cls, model_type: Type[T], items: dict[EntityId, BaseDTO]) -> PRepository[T]:
        obj = cls.__new__(cls)
        obj._items = items
        obj.model_type = model_type
        return obj
    
    def clone(self) -> PRepository[T]:
        return self.__class__.from_dict(self.model_type, copy.deepcopy(self._items))
    
    def create(self, items: list[T]) -> None:
        for item in items:
            self._items[item.entity_id] = to_dto(item)
    
    def read_by_attribute(self, attribute_name: str, values: list[Any]) -> list[T]:
        result: list[T] = []
        for item in self._items.values():
            if getattr(item, attribute_name, None) in values:
                result.append(self.model_type.from_dict(item.model_dump()))
        return result
    
    def read_all(self) -> list[T]:
        return [self.model_type.from_dict(item.model_dump()) for item in self._items.values()]
    
    def update(self, items: list[T]) -> None:
        for item in items:
            self._items[item.entity_id] = to_dto(item)
    
    def delete(self, items: list[T]) -> None:
        for item in items:
            self._items.pop(item.entity_id)
    
    def delete_by_attribute(self, attribute_name: str, values: list[str]) -> None:
        to_delete = [
            EntityId(item.entity_id) # type: ignore
            for item in self._items.values() 
            if getattr(item, attribute_name) in values
        ]
        for entity_id in to_delete:
            self._items.pop(entity_id)
    
    def fill(self, items: list[T]) -> None:
        for item in items:
            self._items[item.entity_id] = to_dto(item)
            
    def load_from_query(self, query: LoadQuery) -> list[T]:
        return [
            self.model_type.from_dict(item.model_dump()) 
            for item in self._items.values()
            if SQLCriteriaEvaluator.evaluate(query.criteria, item)
        ]
    
    def save(self, difference_snapshot: dict[Literal['CREATED', 'UPDATED', 'DELETED'], list[BaseDTO]]) -> None:
        for item in difference_snapshot['CREATED']:
            self.create([self.model_type.from_dict(item.model_dump())])

        for item in difference_snapshot['UPDATED']:
            self.update([self.model_type.from_dict(item.model_dump())])

        for item in difference_snapshot['DELETED']:
            self.delete([self.model_type.from_dict(item.model_dump())])
    
    def get_unique_id(self) -> EntityId:
        return EntityId(str(next(self._id_counter)))


class SQLCriterionEvaluator:
    @staticmethod
    def evaluate(criterion: QueryCriterion, item: BaseDTO) -> bool:
        actual_value = getattr(item, criterion.left_project_by)
        provided_values = [v for v in criterion.value_provider.get()]
        
        if criterion.operator == QueryCriterionOperator.IN:
            return actual_value in provided_values
        elif criterion.operator == QueryCriterionOperator.EQUALS:
            return actual_value == provided_values[0] if provided_values else False
        else:
            raise ValueError(f'Unknown operator: {criterion.operator}')

class SQLCriteriaEvaluator:
    @staticmethod
    def evaluate(criteria: QueryCriteria, item: BaseDTO) -> bool:
        stack: list[bool | QueryCriteriaOperator] = []
        for expr in criteria.expression:
            if isinstance(expr, QueryCriterion):
                stack.append(SQLCriterionEvaluator.evaluate(expr, item))
            elif isinstance(expr, QueryCriteriaOperator):
                stack.append(expr)
        
        # Простая интерпретация без скобок
        result = stack[0]
        for i in range(1, len(stack), 2):
            operator = stack[i]
            next_val = stack[i+1]
            result = result and next_val if operator == QueryCriteriaOperator.AND else result or next_val
        
        if isinstance(result, bool):
            return result
        else:
            raise ValueError(f'Evaluation error: {result}')


@pytest.fixture
def fake_repository() -> Callable[[Type[BaseAggregate], list[BaseAggregate]], PRepository[BaseAggregate]]:
    def factory(model_type: Type[BaseAggregate], items: list[BaseAggregate]) -> PRepository[BaseAggregate]:
        return FakeRepository(model_type, items)
    
    return factory