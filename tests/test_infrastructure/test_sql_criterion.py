import pytest

from shop_project.infrastructure.persistence.query.query_criteria import QueryCriteria
from shop_project.infrastructure.persistence.query.value_container import ValueContainer


def test_correct() -> None:
    criteria = (
        QueryCriteria()
        .criterion_in("id", ValueContainer([1, 2, 3]))
        .and_()
        .criterion_in("status", ValueContainer(["ACTIVE"]))
    )

    criteria.validate()


def test_too_many_criteria() -> None:
    with pytest.raises(ValueError):
        criteria = (
            QueryCriteria()
            .criterion_in("id", ValueContainer([1, 2, 3]))
            .criterion_in("status", ValueContainer(["ACTIVE"]))
        )


def test_too_many_operators() -> None:
    with pytest.raises(ValueError):
        criteria = (
            QueryCriteria().criterion_in("id", ValueContainer([1, 2, 3])).and_().and_()
        )


def test_trailing_operator() -> None:
    criteria = QueryCriteria().criterion_in("id", ValueContainer([1, 2, 3])).and_()

    with pytest.raises(ValueError):
        criteria.validate()
