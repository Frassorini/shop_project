from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends

from shop_project.application.customer.schemas.claim_token_schema import (
    ClaimTokenSchema,
)
from shop_project.application.customer.schemas.purchase_summary_schema import (
    PurchaseSummarySchema,
)
from shop_project.application.employee.commands.purchase_active_employee_service import (
    PurchaseActiveEmployeeService,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.controllers.fastapi.dependencies.auth import get_access_payload

router = APIRouter(route_class=DishkaRoute, prefix="/employee")


@router.post(
    "/purchases/claim",
    response_model=list[PurchaseSummarySchema],
)
async def claim_purchases(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[PurchaseActiveEmployeeService],
    claim_token: ClaimTokenSchema,
) -> list[PurchaseSummarySchema]:
    return await service.claim(
        access_payload=access_payload,
        claim_token=claim_token,
    )
