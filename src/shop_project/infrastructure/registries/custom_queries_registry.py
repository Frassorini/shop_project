from typing import Literal


from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.product import Product
from shop_project.infrastructure.query.custom_query import CustomQuery


class BiggestPurchaseActivesQuery(CustomQuery):
    model_type = PurchaseActive
    return_type: Literal['DOMAIN', 'SCALARS'] = 'DOMAIN'
    def set_args(self) -> None:
        pass


class CountProductsQuery(CustomQuery):
    model_type = Product
    return_type: Literal['DOMAIN', 'SCALARS'] = 'SCALARS'
    def set_args(self) -> None:
        pass
