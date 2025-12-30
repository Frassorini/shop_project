from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Query

from shop_project.application.customer.commands.purchase_active_customer_service import (
    PurchaseActiveCustomerService,
)
from shop_project.application.customer.commands.purchase_draft_customer_service import (
    PurchaseDraftCustomerService,
)
from shop_project.application.customer.queries.purchase_customer_read_service import (
    PurchaseCustomerReadService,
)
from shop_project.application.customer.schemas.claim_token_schema import (
    ClaimTokenSchema,
)
from shop_project.application.customer.schemas.purchase_active_schema import (
    PurchaseActivationSchema,
    PurchaseActiveSchema,
)
from shop_project.application.customer.schemas.purchase_draft_schema import (
    PurchaseDraftSchema,
    SetNewPurchaseDraftItemsSchema,
)
from shop_project.application.customer.schemas.purchase_summary_schema import (
    PurchaseSummarySchema,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.controllers.fastapi.dependencies.auth import get_access_payload

router = APIRouter(route_class=DishkaRoute, prefix="/customer")


@router.post(
    "/claim-token",
    response_model=ClaimTokenSchema,
)
async def get_claim_token(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[PurchaseActiveCustomerService],
) -> ClaimTokenSchema:
    return await service.get_claim_token(access_payload)


@router.post(
    "/purchase-drafts/{purchase_draft_id}/activate",
    response_model=PurchaseActivationSchema,
)
async def activate_purchase_draft(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[PurchaseActiveCustomerService],
    purchase_draft_id: UUID,
) -> PurchaseActivationSchema:
    return await service.activate_draft(
        access_payload=access_payload,
        purchase_draft_id=purchase_draft_id,
    )


@router.post(
    "/purchases/{purchase_active_id}/unclaim",
    response_model=PurchaseSummarySchema,
)
async def unclaim_purchase(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[PurchaseActiveCustomerService],
    purchase_active_id: UUID,
) -> PurchaseSummarySchema:
    return await service.unclaim(
        access_payload=access_payload,
        purchase_active_id=purchase_active_id,
    )


@router.post(
    "/purchase-drafts",
    response_model=PurchaseDraftSchema,
    status_code=201,
)
async def create_purchase_draft(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[PurchaseDraftCustomerService],
) -> PurchaseDraftSchema:
    return await service.create_draft(access_payload)


@router.delete(
    "/purchase-drafts/{draft_id}",
    status_code=204,
)
async def delete_purchase_draft(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[PurchaseDraftCustomerService],
    draft_id: UUID,
) -> None:
    await service.delete_draft(
        access_payload=access_payload,
        draft_id=draft_id,
    )


@router.put(
    "/purchase-drafts/{draft_id}/items",
    response_model=PurchaseDraftSchema,
)
async def set_purchase_draft_items(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[PurchaseDraftCustomerService],
    draft_id: UUID,
    change: SetNewPurchaseDraftItemsSchema,
) -> PurchaseDraftSchema:
    return await service.change_products(
        access_payload=access_payload,
        draft_id=draft_id,
        change=change,
    )


@router.get(
    "/purchase-drafts/by-ids",
    response_model=list[PurchaseDraftSchema],
)
async def get_purchase_drafts_by_ids(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[PurchaseCustomerReadService],
    ids: list[UUID] = Query(...),
) -> list[PurchaseDraftSchema]:
    return await service.get_drafts_by_ids(
        access_payload=access_payload,
        ids=ids,
    )


@router.get(
    "/purchase-actives/by-ids",
    response_model=list[PurchaseActiveSchema],
)
async def get_purchase_actives_by_ids(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[PurchaseCustomerReadService],
    ids: list[UUID] = Query(...),
) -> list[PurchaseActiveSchema]:
    return await service.get_actives_by_ids(
        access_payload=access_payload,
        ids=ids,
    )


@router.get(
    "/purchase-summaries/by-ids",
    response_model=list[PurchaseSummarySchema],
)
async def get_purchase_summaries_by_ids(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[PurchaseCustomerReadService],
    ids: list[UUID] = Query(...),
) -> list[PurchaseSummarySchema]:
    return await service.get_summaries_by_ids(
        access_payload=access_payload,
        ids=ids,
    )


@router.get(
    "/purchase-actives",
    response_model=list[PurchaseActiveSchema],
)
async def list_purchase_actives(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[PurchaseCustomerReadService],
    offset: int = Query(0, ge=0),
    limit: int = Query(20, gt=0, le=100),
) -> list[PurchaseActiveSchema]:
    return await service.get_actives(
        access_payload=access_payload,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/purchase-drafts",
    response_model=list[PurchaseDraftSchema],
)
async def list_purchase_drafts(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[PurchaseCustomerReadService],
    offset: int = Query(0, ge=0),
    limit: int = Query(20, gt=0, le=100),
) -> list[PurchaseDraftSchema]:
    return await service.get_drafts(
        access_payload=access_payload,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/purchase-summaries",
    response_model=list[PurchaseSummarySchema],
)
async def list_purchase_summaries(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[PurchaseCustomerReadService],
    offset: int = Query(0, ge=0),
    limit: int = Query(20, gt=0, le=100),
) -> list[PurchaseSummarySchema]:
    return await service.get_summaries(
        access_payload=access_payload,
        offset=offset,
        limit=limit,
    )
