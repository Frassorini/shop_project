from decimal import Decimal
from enum import Enum

from pydantic import BaseModel

from shop_project.application.exceptions import ApplicationException


class PaymentNotExistsException(ApplicationException):
    pass


class PaymentState(Enum):
    NONEXISTENT = "NONEXISTENT"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"
    PAID = "PAID"
    REFUNDING = "REFUNDING"
    REFUNDED = "REFUNDED"
    FAILED_REFUND = "FAILED_REFUND"


class CreatePaymentRequest(BaseModel):
    payment_id: str
    amount: Decimal


class IPaymentGateway:
    async def get_payment_url(self, payment_id: str) -> str: ...

    async def create_payment_and_get_url(
        self, request: CreatePaymentRequest
    ) -> str: ...

    async def create_payments(self, requests: list[CreatePaymentRequest]) -> None: ...

    async def get_states(self, payment_ids: list[str]) -> dict[str, PaymentState]: ...

    async def start_refunds(self, payment_ids: list[str]) -> None: ...
