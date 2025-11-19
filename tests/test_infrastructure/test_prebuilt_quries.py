from typing import Any, Awaitable, Callable, Coroutine, Literal, Type, TypeVar, cast
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.customer import Customer
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.purchase_summary import PurchaseSummary
from shop_project.domain.escrow_account import EscrowAccount
from shop_project.domain.product import Product
from shop_project.domain.shipment import Shipment
from shop_project.domain.shipment_summary import ShipmentSummary

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWork, UnitOfWorkFactory
from shop_project.infrastructure.exceptions import UnitOfWorkException, ResourcesException

from shop_project.infrastructure.query.queries.prebuilt_queries import (
    CountProductsQuery,
    BiggestPurchaseActivesQuery,
)


DomainObject = TypeVar('DomainObject', bound=BaseAggregate)


@pytest.mark.asyncio
async def test_count_products(product_factory: Callable[..., Product],
                                 uow_factory: UnitOfWorkFactory,
                                 fill_database: Callable[[dict[Type[BaseAggregate], list[BaseAggregate]]], Awaitable[None]],
                                 ) -> None:
    model_type: Type[BaseAggregate] = Product
    
    products: list[Product] = [
        product_factory(name='sausages_1', amount=1, price="1.0"),
        product_factory(name='sausages_2', amount=4, price="1.0"),
        product_factory(name='sausages_3', amount=2, price="1.0"),
        product_factory(name='sausages_4', amount=3, price="1.0"),
    ]
    
    await fill_database({Product: cast(list[BaseAggregate], products)})

    query = CountProductsQuery(lock="NO_LOCK")
    
    async with uow_factory.create(
        QueryBuilder(mutating=False)
        .add_prebuilt(query)
    ) as uow:
        pass
    
    assert query.get_result()[0] == 4
