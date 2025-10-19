from typing import Literal


from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.store_item import StoreItem
from shop_project.infrastructure.query.prebuilt_load_query import PrebuiltLoadQuery


class BiggestPurchaseActivesQuery(PrebuiltLoadQuery):
    model_type = PurchaseActive
    return_type: Literal['DOMAIN', 'SCALARS'] = 'DOMAIN'
    def set_args(self) -> None:
        pass


class CountStoreItemsQuery(PrebuiltLoadQuery):
    model_type = StoreItem
    return_type: Literal['DOMAIN', 'SCALARS'] = 'SCALARS'
    def set_args(self) -> None:
        pass