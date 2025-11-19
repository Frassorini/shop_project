from typing import Any, Awaitable, Callable, Coroutine, Literal, Type, TypeVar, cast
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.shipment import Shipment
from shop_project.domain.entities.shipment_summary import ShipmentSummary

from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.infrastructure.unit_of_work import UnitOfWork, UnitOfWorkFactory
from shop_project.infrastructure.exceptions import UnitOfWorkException, ResourcesException

from shop_project.infrastructure.registries.custom_queries_registry import (
    CountProductsQuery,
    BiggestPurchaseActivesQuery,
)


DomainObject = TypeVar('DomainObject', bound=PersistableEntity)


@pytest.mark.asyncio
async def test_count_products(product_factory: Callable[..., Product],
                                 uow_factory: UnitOfWorkFactory,
                                 fill_database: Callable[[dict[Type[PersistableEntity], list[PersistableEntity]]], Awaitable[None]],
                                 ) -> None:
    model_type: Type[PersistableEntity] = Product
    
    products: list[Product] = [
        product_factory(name='sausages_1', amount=1, price="1.0"),
        product_factory(name='sausages_2', amount=4, price="1.0"),
        product_factory(name='sausages_3', amount=2, price="1.0"),
        product_factory(name='sausages_4', amount=3, price="1.0"),
    ]
    
    await fill_database({Product: cast(list[PersistableEntity], products)})

    query = CountProductsQuery(lock="NO_LOCK")
    
    async with uow_factory.create(
        QueryBuilder(mutating=False)
        .add_prebuilt(query)
    ) as uow:
        pass
    
    assert query.get_result()[0] == 4
