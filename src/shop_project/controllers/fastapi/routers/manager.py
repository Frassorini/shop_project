from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, HTTPException, Query

from shop_project.application.manager.commands.employee_manager_service import (
    EmployeeManagerService,
)
from shop_project.application.manager.commands.product_manager_service import (
    ProductManagerService,
)
from shop_project.application.manager.commands.shipment_manager_service import (
    ShipmentManagerService,
)
from shop_project.application.manager.queries.employee_manager_read_service import (
    EmployeeManagerReadService,
)
from shop_project.application.manager.queries.operation_log_read_service import (
    OperationLogReadService,
)
from shop_project.application.manager.schemas.employee_schema import EmployeeSchema
from shop_project.application.manager.schemas.operation_log_schema import (
    OperationLogSchema,
)
from shop_project.application.manager.schemas.shipment_schema import (
    CreateShipmentSchema,
    ShipmentSchema,
    ShipmentSummarySchema,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.schemas.product_schema import (
    ChangeProductSchema,
    CreateProductSchema,
    ProductSchema,
)
from shop_project.controllers.fastapi.dependencies.auth import get_access_payload

router = APIRouter(route_class=DishkaRoute, prefix="/manager")


@router.post("/products")
async def create_product(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[ProductManagerService],
    product_schema: CreateProductSchema,
) -> ProductSchema:
    return await service.create_product(access_payload, product_schema)


@router.delete("/products/{product_id}")
async def delete_product(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[ProductManagerService],
    product_id: UUID,
) -> None:
    return await service.delete_products(access_payload, [product_id])


@router.put("/products")
async def change_product(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[ProductManagerService],
    product_schema: ChangeProductSchema,
) -> ProductSchema:
    return await service.change_product(access_payload, product_schema)


@router.get("/operation-logs")
async def list_operation_logs(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[OperationLogReadService],
    after: int | None = Query(None, ge=0),
    before: int | None = Query(None, ge=0),
    limit: int = Query(50, ge=1, le=500),
) -> list[OperationLogSchema]:

    if after is not None and before is not None:
        raise HTTPException(
            status_code=400,
            detail="Specify only one of 'after' or 'before'",
        )

    if after is not None:
        return await service.get_after_sequence(
            access_payload=access_payload,
            sequence=after,
            limit=limit,
        )

    if before is not None:
        return await service.get_before_sequence(
            access_payload=access_payload,
            sequence=before,
            limit=limit,
        )

    # дефолт: последние записи
    return await service.get_before_sequence(
        access_payload=access_payload,
        sequence=10**18,  # или max seq
        limit=limit,
    )


@router.post(
    "/shipments",
    response_model=ShipmentSchema,
    status_code=201,
)
async def create_shipment(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[ShipmentManagerService],
    shipment_schema: CreateShipmentSchema,
) -> ShipmentSchema:
    return await service.create_shipment(
        access_payload=access_payload,
        create_shipment_schema=shipment_schema,
    )


@router.post(
    "/shipments/{shipment_id}/cancel",
    response_model=ShipmentSummarySchema,
)
async def cancel_shipment(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[ShipmentManagerService],
    shipment_id: UUID,
) -> ShipmentSummarySchema:
    return await service.cancel_shipment(
        access_payload=access_payload,
        shipment_id=shipment_id,
    )


@router.post(
    "/shipments/{shipment_id}/receive",
    response_model=ShipmentSummarySchema,
)
async def receive_shipment(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[ShipmentManagerService],
    shipment_id: UUID,
) -> ShipmentSummarySchema:
    return await service.receive_shipment(
        access_payload=access_payload,
        shipment_id=shipment_id,
    )


@router.post(
    "/employees/{employee_id}/authorize",
    response_model=EmployeeSchema,
)
async def authorize_employee(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[EmployeeManagerService],
    employee_id: UUID,
) -> EmployeeSchema:
    return await service.authorize_employee(
        access_payload=access_payload,
        employee_id=employee_id,
    )


@router.post(
    "/employees/{employee_id}/unauthorize",
    response_model=EmployeeSchema,
)
async def unauthorize_employee(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[EmployeeManagerService],
    employee_id: UUID,
) -> EmployeeSchema:
    return await service.unauthorize_employee(
        access_payload=access_payload,
        employee_id=employee_id,
    )


@router.get(
    "/employees",
    response_model=list[EmployeeSchema],
)
async def list_employees(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[EmployeeManagerReadService],
    offset: int = Query(0, ge=0),
    limit: int = Query(20, gt=0, le=100),
) -> list[EmployeeSchema]:
    return await service.get(access_payload, limit, offset)


@router.get(
    "/employees/by-ids",
    response_model=list[EmployeeSchema],
)
async def get_employees_by_ids(
    access_payload: Annotated[AccessTokenPayload, Depends(get_access_payload)],
    service: FromDishka[EmployeeManagerReadService],
    ids: list[UUID] = Query(...),
) -> list[EmployeeSchema]:
    return await service.get_by_ids(access_payload, ids)
