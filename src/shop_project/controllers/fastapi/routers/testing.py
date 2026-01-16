from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from shop_project.application.payments.commands.payment_service import PaymentService

router = APIRouter(route_class=DishkaRoute, prefix="/_testing")


@router.post("/payments/{payment_id}/confirm")
async def confirm_payment(
    service: FromDishka[PaymentService], payment_id: UUID
) -> None:
    await service.confirm_payment(payment_id)


@router.post("/payments/{payment_id}/cancel")
async def cancel_payment(service: FromDishka[PaymentService], payment_id: UUID) -> None:
    await service.cancel_payment(payment_id)


@router.post("/payments/{payment_id}/confirm-refund")
async def confirm_refund(service: FromDishka[PaymentService], payment_id: UUID) -> None:
    await service.confirm_refund(payment_id)


@router.post("/payments/{payment_id}/finalize-not-paid")
async def finalize_not_paid(
    service: FromDishka[PaymentService], payment_id: UUID
) -> None:
    await service.finalize_not_paid(payment_id)
