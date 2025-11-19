from decimal import Decimal
from typing import Callable

import pytest

from shop_project.shared.entity_id import EntityId
from shop_project.domain.entities.product import Product
from tests.helpers import AggregateContainer


@pytest.fixture
def product_factory(unique_id_factory: Callable[[], EntityId]) -> Callable[..., Product]:
    
    def fact(*, name: str, 
             amount: int, 
             price: Decimal) -> Product:

        return Product(unique_id_factory(), name=name, amount=amount, price=price)
    
    return fact


@pytest.fixture
def product_container_factory(unique_id_factory: Callable[[], EntityId]) -> Callable[..., AggregateContainer]:
    
    def fact(*, name: str, 
             amount: int, 
             price: Decimal) -> AggregateContainer:

        product = Product(unique_id_factory(), name=name, amount=amount, price=price)

        return AggregateContainer(aggregate=product, dependencies={})
    
    return fact


@pytest.fixture
def potatoes_product_1(product_factory: Callable[..., Product]) -> Callable[[], Product]:
    
    def fact(*, price: float | None = None) -> Product:
        if price is None:
            price = 1

        return product_factory(name='potatoes', amount=1, price=price)
    
    return fact


@pytest.fixture
def potatoes_product_10(product_factory: Callable[..., Product]) -> Callable[[], Product]:
    
    def fact(*, price: float | None = None) -> Product:
        if price is None:
            price = 1

        return product_factory(name='potatoes', amount=10, price=price)
    
    return fact


@pytest.fixture
def sausages_product_1(product_factory: Callable[..., Product]) -> Callable[[], Product]:
    
    def fact(*, price: float | None = None) -> Product:
        if price is None:
            price = 1

        return product_factory(name='sausages', amount=1, price=price)
    
    return fact


@pytest.fixture
def sausages_product_10(product_factory: Callable[..., Product]) -> Callable[[], Product]:
    
    def fact(*, price: float | None = None) -> Product:
        if price is None:
            price = 1

        return product_factory(name='sausages', amount=10, price=price)
    
    return fact