from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query

from shop_project.application.customer.queries.catalogue_customer_read_service import (
    CatalogueCustomerReadService,
)
from shop_project.application.shared.schemas.product_schema import (
    ProductSchema,
)

router = APIRouter(route_class=DishkaRoute, prefix="")


@router.get(
    "/catalogue/products/by-ids",
    response_model=list[ProductSchema],
)
async def get_catalogue_products_by_ids(
    service: FromDishka[CatalogueCustomerReadService],
    ids: list[UUID] = Query(...),
) -> list[ProductSchema]:
    return await service.get_products_by_ids(ids)


@router.get(
    "/catalogue/products",
    response_model=list[ProductSchema],
)
async def list_catalogue_products(
    service: FromDishka[CatalogueCustomerReadService],
    offset: int = Query(0, ge=0),
    limit: int = Query(20, gt=0, le=100),
) -> list[ProductSchema]:
    return await service.get_products(
        offset=offset,
        limit=limit,
    )
