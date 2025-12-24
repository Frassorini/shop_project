from typing import Any, Literal

from sqlalchemy import func, select

from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.infrastructure.persistence.database.models.product import (
    Product as ProductORM,
)
from shop_project.infrastructure.persistence.query.custom_query import CustomQuery


class BiggestPurchaseActivesQuery(CustomQuery):
    model_type = PurchaseActive
    return_type: Literal["DOMAIN", "SCALARS"] = "DOMAIN"

    def set_args(self) -> None:
        pass

    def compile_sqlalchemy(self) -> Any:
        pass


class CountProductsQuery(CustomQuery):
    model_type = Product
    return_type: Literal["DOMAIN", "SCALARS"] = "SCALARS"

    def set_args(self) -> None:
        pass

    def compile_sqlalchemy(self) -> Any:
        return select(func.count()).select_from(ProductORM)
