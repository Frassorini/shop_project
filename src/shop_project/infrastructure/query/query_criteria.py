from enum import Enum
from typing import Any, Self, Type

from sqlalchemy import BinaryExpression, Column, ColumnElement, and_, or_
from sqlalchemy.sql import true
from shop_project.exceptions import QueryPlanException
from shop_project.infrastructure.query.p_value_provider import PValueProvider
from shop_project.infrastructure.database.models.base import Base as BaseORM


class QueryCriterionOperator(Enum):
    IN = 'IN'
    GREATER_THAN = 'GREATER_THAN'
    

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
    def greater_than(cls, project_by: str, value_provider: PValueProvider) -> Self:
        obj = cls.__new__(cls)
        cls.__init__(obj, project_by, QueryCriterionOperator.GREATER_THAN, value_provider)
        
        return obj
    
    def to_sqlalchemy(self, model: Type[BaseORM]) -> BinaryExpression[Any]:
        column: Column[Any] = getattr(model, self.left_project_by) 
        if self.operator == QueryCriterionOperator.IN:
            return column.in_(self.value_provider.get())
        elif self.operator == QueryCriterionOperator.GREATER_THAN:
            return column > self.value_provider.get()[0]
        else:
            raise QueryPlanException(f'Unknown operator: {self.operator}')


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
    
    @property
    def is_empty(self) -> bool:
        return len(self.criteria) == 0 and len(self.operators) == 0
    
    def validate(self) -> None:
        if len(self.criteria) == 0 and len(self.operators) == 0:
            return
        
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
    
    def criterion_greater_than(self, project_by: str, value: PValueProvider) -> Self:
        return self.criterion(QueryCriterion.greater_than(project_by, value))
    
    
    def and_(self) -> Self:
        self._validate_can_add_operator()
        self.operators.append(QueryCriteriaOperator.AND)
        return self
    
    def or_(self) -> Self:
        self._validate_can_add_operator()
        self.operators.append(QueryCriteriaOperator.OR)
        return self
    
    
    def to_sqlalchemy(self, model: Type[BaseORM]) -> ColumnElement[bool]:
        """
        Преобразует набор критериев в одно SQLAlchemy-выражение.
        """
        self.validate()
        if len(self.criteria) == 0:
            return true()
        
        # Берём первый критерий как базу
        result = self.criteria[0].to_sqlalchemy(model)

        # Дальше проходим попарно по (оператор, критерий)
        for operator, criterion in zip(self.operators, self.criteria[1:]):
            right = criterion.to_sqlalchemy(model)

            if operator == QueryCriteriaOperator.AND:
                result = and_(result, right)
            elif operator == QueryCriteriaOperator.OR:
                result = or_(result, right)
            else:
                raise QueryPlanException(f"Unknown operator: {operator}")

        return result
