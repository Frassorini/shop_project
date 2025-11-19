from typing import Any, Type

from plum import overload, dispatch
from sqlalchemy import func
from sqlalchemy.orm import aliased, contains_eager, joinedload
from sqlalchemy.sql import select, delete, insert, update

from shop_project.application.dto.base_dto import BaseDTO
from shop_project.application.dto.customer_dto import CustomerDTO
from shop_project.application.dto.purchase_draft_dto import PurchaseDraftDTO
from shop_project.application.dto.purchase_active_dto import PurchaseActiveDTO
from shop_project.application.dto.purchase_summary_dto import PurchaseSummaryDTO
from shop_project.application.dto.escrow_account_dto import EscrowAccountDTO
from shop_project.application.dto.product_dto import ProductDTO
from shop_project.application.dto.shipment_dto import ShipmentDTO
from shop_project.application.dto.shipment_summary_dto import ShipmentSummaryDTO

from shop_project.infrastructure.database.models.customer import Customer as CustomerORM
from shop_project.infrastructure.database.models.purchase_draft import PurchaseDraft as PurchaseDraftORM, PurchaseDraftItem as PurchaseDraftItemORM
from shop_project.infrastructure.database.models.purchase_active import PurchaseActive as PurchaseActiveORM, PurchaseActiveItem as PurchaseActiveItemORM
from shop_project.infrastructure.database.models.purchase_summary import PurchaseSummary as PurchaseSummaryORM, PurchaseSummaryItem as PurchaseSummaryItemORM
from shop_project.infrastructure.database.models.escrow_account import EscrowAccount as EscrowAccountORM
from shop_project.infrastructure.database.models.product import Product as ProductORM
from shop_project.infrastructure.database.models.shipment import Shipment as ShipmentORM, ShipmentItem as ShipmentItemORM
from shop_project.infrastructure.database.models.shipment_summary import ShipmentSummary as ShipmentSummaryORM, ShipmentSummaryItem as ShipmentSummaryItemORM

from shop_project.domain.persistable_entity import PersistableEntity
from shop_project.domain.customer import Customer
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.purchase_summary import PurchaseSummary
from shop_project.domain.escrow_account import EscrowAccount
from shop_project.domain.product import Product
from shop_project.domain.shipment import Shipment
from shop_project.domain.shipment_summary import ShipmentSummary

from shop_project.infrastructure.query.base_query import BaseQuery, QueryLock
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery
from shop_project.infrastructure.registries.custom_queries_registry import (
    CountProductsQuery,
    BiggestPurchaseActivesQuery,
)

def _apply_lock(query: Any, lock: QueryLock, of: list[Any]):
    if lock == QueryLock.EXCLUSIVE:
        return query.with_for_update(of=of)
    elif lock == QueryLock.SHARED:
        return query.with_for_update(read=True, of=of)
    return query


@overload
def _compile_composed_query(model_type: Type[Customer], query: ComposedQuery) -> Any:
    base_query = (
        select(CustomerORM)
        .where(query.criteria.to_sqlalchemy(CustomerORM))
    )
    return _apply_lock(base_query, query.lock, [CustomerORM])

@overload
def _compile_composed_query(model_type: Type[PurchaseDraft], query: ComposedQuery) -> Any:
    item_alias = aliased(PurchaseDraftItemORM, name="cart_item")
    
    base_query = (
        select(PurchaseDraftORM)
        .outerjoin(item_alias, PurchaseDraftORM.items)
        .where(query.criteria.to_sqlalchemy(PurchaseDraftORM))
        .options(joinedload(PurchaseDraftORM.items))
    )
    return _apply_lock(base_query, query.lock, [PurchaseDraftORM, item_alias])

@overload
def _compile_composed_query(model_type: Type[PurchaseActive], query: ComposedQuery) -> Any:
    item_alias = aliased(PurchaseActiveItemORM, name="customer_order_item")
    
    base_query = (
        select(PurchaseActiveORM)
        .outerjoin(item_alias, PurchaseActiveORM.items)
        .where(query.criteria.to_sqlalchemy(PurchaseActiveORM))
        .options(joinedload(PurchaseActiveORM.items))
    )
    return _apply_lock(base_query, query.lock, [PurchaseActiveORM, item_alias])

@overload
def _compile_composed_query(model_type: Type[PurchaseSummary], query: ComposedQuery) -> Any:
    item_alias = aliased(PurchaseSummaryItemORM, name="purchase_summary_item")
    
    base_query = (
        select(PurchaseSummaryORM)
        .outerjoin(item_alias, PurchaseSummaryORM.items)
        .where(query.criteria.to_sqlalchemy(PurchaseSummaryORM))
        .options(joinedload(PurchaseSummaryORM.items))
    )
    return _apply_lock(base_query, query.lock, [PurchaseSummaryORM, item_alias])

@overload
def _compile_composed_query(model_type: Type[EscrowAccount], query: ComposedQuery) -> Any:
    base_query = (
        select(EscrowAccountORM)
        .where(query.criteria.to_sqlalchemy(EscrowAccountORM))
    )
    return _apply_lock(base_query, query.lock, [EscrowAccountORM])


@overload
def _compile_composed_query(model_type: Type[Product], query: ComposedQuery) -> Any:
    base_query = (
        select(ProductORM)
        .where(query.criteria.to_sqlalchemy(ProductORM))
    )
    return _apply_lock(base_query, query.lock, [ProductORM])

@overload
def _compile_composed_query(model_type: Type[Shipment], query: ComposedQuery) -> Any:
    item_alias = aliased(ShipmentItemORM, name="supplier_order_item")
    
    base_query = (
        select(ShipmentORM)
        .outerjoin(item_alias, ShipmentORM.items)
        .where(query.criteria.to_sqlalchemy(ShipmentORM))
        .options(joinedload(ShipmentORM.items))
    )
    return _apply_lock(base_query, query.lock, [ShipmentORM, item_alias])

@overload
def _compile_composed_query(model_type: Type[ShipmentSummary], query: ComposedQuery) -> Any:
    item_alias = aliased(ShipmentSummaryItemORM, name="shipment_summary_item")
    
    base_query = (
        select(ShipmentSummaryORM)
        .outerjoin(item_alias, ShipmentSummaryORM.items)
        .where(query.criteria.to_sqlalchemy(ShipmentSummaryORM))
        .options(joinedload(ShipmentSummaryORM.items))
    )
    return _apply_lock(base_query, query.lock, [ShipmentSummaryORM, item_alias])

@dispatch
def _compile_composed_query(model_type: Type[PersistableEntity], query: ComposedQuery) -> Any:
    pass


@overload
def _compile_custom_query(query: BiggestPurchaseActivesQuery) -> Any:
    pass

@overload
def _compile_custom_query(query: CountProductsQuery) -> Any:
    return (
        select(func.count()).select_from(ProductORM)
    )

@dispatch
def _compile_custom_query(query: CustomQuery) -> Any:
    pass


@overload
def compile_query(query: ComposedQuery) -> Any:
    return _compile_composed_query(query.model_type, query) # type: ignore

@overload
def compile_query(query: CustomQuery) -> Any:
    return _compile_custom_query(query) # type: ignore

@overload
def compile_query(query: BaseQuery) -> Any:
    pass

@dispatch
def compile_query(query: BaseQuery) -> Any:
    pass