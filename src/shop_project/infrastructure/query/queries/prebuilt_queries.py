from typing import Literal


from shop_project.domain.customer_order import CustomerOrder
from shop_project.domain.store_item import StoreItem
from shop_project.infrastructure.query.prebuilt_load_query import PrebuiltLoadQuery


class BiggestCustomerOrdersQuery(PrebuiltLoadQuery):
    model_type = CustomerOrder
    return_type: Literal['DOMAIN', 'SCALARS'] = 'DOMAIN'
    def set_args(self) -> None:
        pass


class CountStoreItemsQuery(PrebuiltLoadQuery):
    model_type = StoreItem
    return_type: Literal['DOMAIN', 'SCALARS'] = 'SCALARS'
    def set_args(self) -> None:
        pass