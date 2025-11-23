from typing import Callable
from uuid import uuid4

import pytest

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.infrastructure.exceptions import QueryPlanException
from shop_project.infrastructure.query.composed_query import ComposedQuery, QueryLock
from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.infrastructure.query.query_criteria import QueryCriteria
from shop_project.infrastructure.query.query_plan import QueryPlan
from shop_project.infrastructure.query.value_container import ValueContainer
from shop_project.infrastructure.query.value_extractor import ValueExtractor
from shop_project.infrastructure.registries.custom_queries_registry import (
    CountProductsQuery,
)


def test_empty_source():
    with pytest.raises(QueryPlanException):
        QueryBuilder(mutating=False).load(PurchaseDraft).build()


def test_load_from_attribute():
    query = ComposedQuery(
        PurchaseDraft,
        QueryCriteria().criterion_in("entity_id", ValueContainer(["1"])),
        QueryLock.NO_LOCK,
    )

    query_built: QueryPlan = (
        QueryBuilder(mutating=False)
        .load(PurchaseDraft)
        .from_attribute("entity_id", ["1"])
        .no_lock()
        .build()
    )

    assert isinstance(query_built.queries[0], ComposedQuery) and query_built.queries[0]
    assert (
        query_built.queries[0].criteria.criteria[0].value_provider.get()
        == query.criteria.criteria[0].value_provider.get()
    )
    assert query_built.queries[0].model_type == query.model_type


def test_load_from_id():
    uuid_id = uuid4()

    query = ComposedQuery(
        PurchaseDraft,
        QueryCriteria().criterion_in("entity_id", ValueContainer([uuid_id])),
        QueryLock.NO_LOCK,
    )

    query_built: QueryPlan = (
        QueryBuilder(mutating=False)
        .load(PurchaseDraft)
        .from_id([uuid_id])
        .no_lock()
        .build()
    )

    assert isinstance(query_built.queries[0], ComposedQuery) and query_built.queries[0]
    assert (
        query_built.queries[0].criteria.criteria[0].value_provider.get()
        == query.criteria.criteria[0].value_provider.get()
    )
    assert query_built.queries[0].model_type == query.model_type


def test_load_from_previous(purchase_draft_factory: Callable[[], PurchaseDraft]):
    purchase_active = purchase_draft_factory()

    query = ComposedQuery(
        PurchaseDraft,
        QueryCriteria().criterion_in(
            "entity_id", ValueContainer([purchase_active.entity_id])
        ),
        QueryLock.NO_LOCK,
    )
    query.load([purchase_active])
    query_product = ComposedQuery(
        Product,
        QueryCriteria().criterion_in(
            "entity_id",
            ValueExtractor(
                query, lambda x: [item.product_id for item in x.get_items()]
            ),
        ),
        QueryLock.NO_LOCK,
    )

    query_builder = QueryBuilder(mutating=False).load(Product)
    query_builder.query_plan.queries.append(query)
    query_built: QueryPlan = query_builder.from_previous().no_lock().build()

    assert isinstance(query_built.queries[1], ComposedQuery) and query_built.queries[0]
    assert (
        query_built.queries[1].criteria.criteria[0].value_provider.get()
        == query_product.criteria.criteria[0].value_provider.get()
    )
    assert query_built.queries[1].model_type == query_product.model_type


def test_lock_violation():
    uuid_id = uuid4()

    with pytest.raises(QueryPlanException):
        QueryBuilder(mutating=True).load(PurchaseDraft).from_id(
            [uuid_id]
        ).no_lock().build()

    with pytest.raises(QueryPlanException):
        QueryBuilder(mutating=False).load(PurchaseDraft).from_id(
            [uuid_id]
        ).for_update().build()


def test_correct_locking_load_order():
    plan: QueryPlan = (
        QueryBuilder(mutating=True)
        .load(Customer)
        .from_id([uuid4()])
        .for_share()
        .load(PurchaseDraft)
        .from_previous()
        .for_share()
        .load(Product)
        .from_previous(1)
        .for_update()
        .build()
    )


def xtest_wrong_locking_load_order():
    with pytest.raises(QueryPlanException):
        plan: QueryPlan = (
            QueryBuilder(mutating=True)
            .load(PurchaseDraft)
            .from_id([uuid4()])
            .for_share()
            .load(Customer)
            .from_previous()
            .for_share()
            .load(Product)
            .from_previous()
            .for_update()
            .build()
        )


def test_prebuilt_query():
    query = (
        QueryBuilder(mutating=False)
        .add_prebuilt(CountProductsQuery(lock="NO_LOCK"))
        .build()
    )
    assert len(query.queries) == 1
