from enum import Enum
from typing import Any, Self
from shop_project.exceptions import QueryPlanException
from shop_project.infrastructure.query.p_value_provider import PValueProvider


class QueryCriterionOperator(Enum):
    IN = 'IN'
    EQUALS = 'EQUALS'
    

class QueryCriteriaOperator(Enum):
    AND = 'AND'
    OR = 'OR'


class QueryCriterion:
    def __init__(self, left_project_by: str, operator: QueryCriterionOperator, value_provider: PValueProvider) -> None:
        self.left_project_by: str = left_project_by
        self.operator: QueryCriterionOperator = operator
        self.value_provider: PValueProvider = value_provider
    
    @classmethod
    def is_in(cls, project_by: str, value_provider: PValueProvider) -> Self:
        obj = cls.__new__(cls)
        cls.__init__(obj, project_by, QueryCriterionOperator.IN, value_provider)
        
        return obj
    
    @classmethod
    def equals(cls, project_by: str, value_provider: PValueProvider) -> Self:
        obj = cls.__new__(cls)
        cls.__init__(obj, project_by, QueryCriterionOperator.EQUALS, value_provider)
        
        return obj


class QueryCriteria:
    def __init__(self) -> None:
        self.criteria: list[QueryCriterion] = []
        self.operators: list[QueryCriteriaOperator] = []
    
    @property
    def expression(self) -> list[QueryCriterion | QueryCriteriaOperator]:
        result: list[QueryCriterion | QueryCriteriaOperator] = []
        for criterion, operator in zip(self.criteria, self.operators):
            result.append(criterion)
            result.append(operator)
        result.append(self.criteria[-1])
    
        return result
    
    def validate(self) -> None:
        if not (len(self.criteria) - len(self.operators)) == 1:
            raise ValueError("Invalid criteria")
    
    def _validate_can_add_criterion(self) -> None:
        if not len(self.criteria) == len(self.operators):
            raise ValueError("Cannot add criterion")
    
    def _validate_can_add_operator(self) -> None:
        if not (len(self.criteria) - len(self.operators)) == 1:
            raise ValueError("Cannot add operator")
    
    
    def criterion(self, criterion: QueryCriterion) -> Self:
        self._validate_can_add_criterion()
        self.criteria.append(criterion)
        return self
    
    def criterion_in(self, project_by: str, value: PValueProvider) -> Self:
        return self.criterion(QueryCriterion.is_in(project_by, value))
    
    def criterion_equals(self, project_by: str, value: PValueProvider) -> Self:
        return self.criterion(QueryCriterion.equals(project_by, value))
    
    
    def and_(self) -> Self:
        self._validate_can_add_operator()
        self.operators.append(QueryCriteriaOperator.AND)
        return self
    
    def or_(self) -> Self:
        self._validate_can_add_operator()
        self.operators.append(QueryCriteriaOperator.OR)
        return self