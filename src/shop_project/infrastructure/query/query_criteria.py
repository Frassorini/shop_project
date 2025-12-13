from enum import Enum
from typing import Any, Self, Type

from sqlalchemy import (
    BinaryExpression,
    Column,
    ColumnElement,
    and_,
    exists,
    or_,
    select,
)
from sqlalchemy.orm import aliased
from sqlalchemy.sql import true

from shop_project.infrastructure.database.models.base import Base as BaseORM
from shop_project.infrastructure.exceptions import QueryPlanException
from shop_project.infrastructure.query.p_value_provider import PValueProvider


class QueryCriterionOperator(Enum):
    IN = "IN"
    GREATER_THAN = "GREATER_THAN"


class QueryCriteriaOperator(Enum):
    AND = "AND"
    OR = "OR"


class QueryCriterion:
    def __init__(
        self,
        left_project_by: str,
        operator: QueryCriterionOperator,
        value_provider: PValueProvider,
    ) -> None:
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
        cls.__init__(
            obj, project_by, QueryCriterionOperator.GREATER_THAN, value_provider
        )

        return obj

    def to_sqlalchemy(
        self,
        model: Type[BaseORM],
        *,
        child_tables: dict[str, Any] | None = None,
        parent_refs: dict[str, str] | None = None,
    ) -> ColumnElement[bool]:

        # --- простой атрибут родителя ---
        if "." not in self.left_project_by:
            column: Column[Any] = getattr(model, self.left_project_by)
            return self._apply_operator(column, self.value_provider.get())

        # --- nested child ---
        if child_tables is None or parent_refs is None:
            raise QueryPlanException(
                f"Cannot filter by nested attribute {self.left_project_by} without aliases and parent_refs"
            )

        container_name, field_name = self.left_project_by.split(".", 1)

        if container_name not in child_tables:
            raise QueryPlanException(f"Unknown child container '{container_name}'")

        if container_name not in parent_refs:
            raise QueryPlanException(f"No parent ref for child '{container_name}'")

        child_alias = aliased(
            child_tables[container_name],
            name=f"{child_tables[container_name].__tablename__}_filter",
        )
        parent_fk_field = parent_refs[container_name]

        child_fk_column = getattr(child_alias, parent_fk_field)
        parent_pk_column = getattr(model, "entity_id")
        child_column = getattr(child_alias, field_name)

        return exists(
            select(1)
            .select_from(child_alias)
            .where(
                child_fk_column == parent_pk_column,
                self._apply_operator(child_column, self.value_provider.get()),
            )
        )

    def _apply_operator(
        self,
        column: Column[Any],
        values: list[Any],
    ) -> BinaryExpression[Any]:
        if self.operator == QueryCriterionOperator.IN:
            return column.in_(values)
        elif self.operator == QueryCriterionOperator.GREATER_THAN:
            return column > values[0]
        else:
            raise QueryPlanException(f"Unknown operator: {self.operator}")


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

    def to_sqlalchemy(
        self,
        model: Type[BaseORM],
        *,
        child_tables: dict[str, Any] | None = None,
        parent_refs: dict[str, Any] | None = None,
    ) -> ColumnElement[bool]:
        self.validate()
        if len(self.criteria) == 0:
            return true()

        result = self.criteria[0].to_sqlalchemy(
            model, child_tables=child_tables, parent_refs=parent_refs
        )

        for operator, criterion in zip(self.operators, self.criteria[1:]):
            right = criterion.to_sqlalchemy(
                model, child_tables=child_tables, parent_refs=parent_refs
            )
            if operator == QueryCriteriaOperator.AND:
                result = and_(result, right)
            elif operator == QueryCriteriaOperator.OR:
                result = or_(result, right)
            else:
                raise QueryPlanException(f"Unknown operator: {operator}")

        return result
