from typing import Any, Type

from plum import overload, dispatch
from sqlalchemy import func
from sqlalchemy.orm import aliased, contains_eager, joinedload
from sqlalchemy.sql import select, delete, insert, update

from shop_project.application.dto.customer_dto import CustomerDTO
from shop_project.application.dto.store_item_dto import StoreItemDTO
from shop_project.application.dto.store_dto import StoreDTO
from shop_project.application.dto.cart_dto import CartDTO
from shop_project.application.dto.customer_order_dto import CustomerOrderDTO
from shop_project.application.dto.supplier_order_dto import SupplierOrderDTO
from shop_project.application.dto.base_dto import BaseDTO

from shop_project.infrastructure.database.models.customer import Customer as CustomerORM
from shop_project.infrastructure.database.models.store_item import StoreItem as StoreItemORM
from shop_project.infrastructure.database.models.store import Store as StoreORM
from shop_project.infrastructure.database.models.customer_order import CustomerOrder as CustomerOrderORM, CustomerOrderItem as CustomerOrderItemORM
from shop_project.infrastructure.database.models.supplier_order import SupplierOrder as SupplierOrderORM, SupplierOrderItem as SupplierOrderItemORM
from shop_project.infrastructure.database.models.cart import Cart as CartORM, CartItem as CartItemORM

from shop_project.domain.customer import Customer
from shop_project.domain.store_item import StoreItem
from shop_project.domain.customer_order import CustomerOrder
from shop_project.domain.supplier_order import SupplierOrder
from shop_project.domain.store import Store
from shop_project.domain.cart import Cart
from shop_project.domain.base_aggregate import BaseAggregate

from shop_project.infrastructure.query.base_load_query import BaseLoadQuery, QueryLock
from shop_project.infrastructure.query.domain_load_query import DomainLoadQuery
from shop_project.infrastructure.query.prebuilt_load_query import PrebuiltLoadQuery
from shop_project.infrastructure.query.queries.prebuilt_queries import (
    CountStoreItemsQuery,
    BiggestCustomerOrdersQuery,
)

def _apply_lock(query: Any, lock: QueryLock, of: list[Any]):
    if lock == QueryLock.EXCLUSIVE:
        return query.with_for_update(of=of)
    elif lock == QueryLock.SHARED:
        return query.with_for_update(read=True, of=of)
    return query


@overload
def _translate_domain(model_type: Type[Customer], query: DomainLoadQuery) -> Any:
    base_query = (
        select(CustomerORM)
        .where(query.criteria.to_sqlalchemy(CustomerORM))
    )
    return _apply_lock(base_query, query.lock, [CustomerORM])

@overload
def _translate_domain(model_type: Type[StoreItem], query: DomainLoadQuery) -> Any:
    base_query = (
        select(StoreItemORM)
        .where(query.criteria.to_sqlalchemy(StoreItemORM))
    )
    return _apply_lock(base_query, query.lock, [StoreItemORM])

@overload
def _translate_domain(model_type: Type[Store], query: DomainLoadQuery) -> Any:
    base_query = (
        select(StoreORM)
        .where(query.criteria.to_sqlalchemy(StoreORM))
    )
    return _apply_lock(base_query, query.lock, [StoreORM])

@overload
def _translate_domain(model_type: Type[CustomerOrder], query: DomainLoadQuery) -> Any:
    item_alias = aliased(CustomerOrderItemORM, name="customer_order_item")
    
    base_query = (
        select(CustomerOrderORM)
        .outerjoin(item_alias, CustomerOrderORM.items)
        .where(query.criteria.to_sqlalchemy(CustomerOrderORM))
        .options(joinedload(CustomerOrderORM.items))
    )
    return _apply_lock(base_query, query.lock, [CustomerOrderORM, item_alias])

@overload
def _translate_domain(model_type: Type[SupplierOrder], query: DomainLoadQuery) -> Any:
    item_alias = aliased(SupplierOrderItemORM, name="supplier_order_item")
    
    base_query = (
        select(SupplierOrderORM)
        .outerjoin(item_alias, SupplierOrderORM.items)
        .where(query.criteria.to_sqlalchemy(SupplierOrderORM))
        .options(joinedload(SupplierOrderORM.items))
    )
    return _apply_lock(base_query, query.lock, [SupplierOrderORM, item_alias])

@overload
def _translate_domain(model_type: Type[Cart], query: DomainLoadQuery) -> Any:
    item_alias = aliased(CartItemORM, name="cart_item")
    
    base_query = (
        select(CartORM)
        .outerjoin(item_alias, CartORM.items)
        .where(query.criteria.to_sqlalchemy(CartORM))
        .options(joinedload(CartORM.items))
    )
    return _apply_lock(base_query, query.lock, [CartORM, item_alias])

@dispatch
def _translate_domain(model_type: Type[BaseAggregate], query: DomainLoadQuery) -> Any:
    pass


@overload
def _translate_prebuilt(query: BiggestCustomerOrdersQuery) -> Any:
    pass

@overload
def _translate_prebuilt(query: CountStoreItemsQuery) -> Any:
    return (
        select(func.count()).select_from(StoreItemORM)
    )

@dispatch
def _translate_prebuilt(query: PrebuiltLoadQuery) -> Any:
    pass


@overload
def translate(query: DomainLoadQuery) -> Any:
    return _translate_domain(query.model_type, query) # type: ignore

@overload
def translate(query: PrebuiltLoadQuery) -> Any:
    return _translate_prebuilt(query) # type: ignore

@overload
def translate(query: BaseLoadQuery) -> Any:
    pass

@dispatch
def translate(query: BaseLoadQuery) -> Any:
    pass