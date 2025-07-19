from itertools import count
from typing import Any, Callable, Literal, Type, TypeVar

import pytest
from shop_project.application.interfaces.p_repository import PRepository
from shop_project.domain.p_aggregate import PAggregate
import copy

from shop_project.infrastructure.query.load_query import LoadQuery
from shop_project.infrastructure.query.query_criteria import QueryCriteriaOperator, QueryCriterion, QueryCriteria, QueryCriterionOperator
from shop_project.shared.entity_id import EntityId


T = TypeVar('T', bound=PAggregate)


class FakeRepository(PRepository[T]):    
    def __init__(self, model_type: Type[T], items: list[T]) -> None:
        self.model_type: Type[T] = model_type
        self._items: dict[EntityId, dict[str, str]] = {}
        self.fill(items)
        self._id_counter = count(start=1)
    
    @classmethod
    def from_dict(cls, model_type: Type[T], items: dict[EntityId, dict[str, str]]) -> PRepository[T]:
        obj = cls.__new__(cls)
        obj._items = items
        obj.model_type = model_type
        return obj
    
    def clone(self) -> PRepository[T]:
        return self.__class__.from_dict(self.model_type, copy.deepcopy(self._items))
    
    def create(self, items: list[T]) -> None:
        for item in items:
            self._items[item.entity_id] = item.snapshot()
    
    def read_by_attribute(self, attribute_name: str, values: list[str]) -> list[T]:
        result: list[T] = []
        for item in self._items.values():
            if item[attribute_name] in values:
                result.append(self.model_type.from_snapshot(item))
        return result
    
    def read_all(self) -> list[T]:
        return [self.model_type.from_snapshot(item) for item in self._items.values()]
    
    def update(self, items: list[T]) -> None:
        for item in items:
            self._items[item.entity_id] = item.snapshot()
    
    def delete(self, items: list[T]) -> None:
        for item in items:
            self._items.pop(item.entity_id)
    
    def delete_by_attribute(self, attribute_name: str, values: list[str]) -> None:
        to_delete = [
            EntityId(item['entity_id'])
            for item in self._items.values() 
            if getattr(item, attribute_name) in values
        ]
        for entity_id in to_delete:
            self._items.pop(entity_id)
    
    def fill(self, items: list[T]) -> None:
        for item in items:
            self._items[item.entity_id] = item.snapshot()
            
    def load_from_query(self, query: LoadQuery) -> list[T]:
        return [
            self.model_type.from_snapshot(item) 
            for item in self._items.values()
            if SQLCriteriaEvaluator.evaluate(query.criteria, item)
        ]
    
    def save(self, difference_snapshot: dict[Literal['CREATED', 'UPDATED', 'DELETED'], list[dict[str, str]]]) -> None:
        for item in difference_snapshot['CREATED']:
            self.create([self.model_type.from_snapshot(item)])

        for item in difference_snapshot['UPDATED']:
            self.update([self.model_type.from_snapshot(item)])

        for item in difference_snapshot['DELETED']:
            self.delete([self.model_type.from_snapshot(item)])
    
    def get_unique_id(self) -> EntityId:
        return EntityId(str(next(self._id_counter)))


class SQLCriterionEvaluator:
    @staticmethod
    def evaluate(criterion: QueryCriterion, item: dict[str, str]) -> bool:
        actual_value = item[criterion.left_project_by]
        provided_values = [v for v in criterion.value_provider.get()]
        
        if criterion.operator == QueryCriterionOperator.IN:
            return actual_value in provided_values
        elif criterion.operator == QueryCriterionOperator.EQUALS:
            return actual_value == provided_values[0] if provided_values else False
        else:
            raise ValueError(f'Unknown operator: {criterion.operator}')

class SQLCriteriaEvaluator:
    @staticmethod
    def evaluate(criteria: QueryCriteria, item: dict[str, str]) -> bool:
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
def fake_repository() -> Callable[[Type[PAggregate], list[PAggregate]], PRepository[PAggregate]]:
    def factory(model_type: Type[PAggregate], items: list[PAggregate]) -> PRepository[PAggregate]:
        return FakeRepository(model_type, items)
    
    return factory