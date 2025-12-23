from shop_project.application.interfaces.interface_payment_gateway import (
    CreatePaymentRequest,
    IPaymentGateway,
    PaymentNotExistsException,
    PaymentState,
)


class InMemoryPaymentGateway(IPaymentGateway):
    def __init__(self) -> None:
        self.map: dict[str, PaymentState] = {}

    async def get_payment_url(self, payment_id: str) -> str:
        if payment_id not in self.map:
            raise PaymentNotExistsException
        return f"example.com/payments/{payment_id}"

    async def create_payment_and_get_url(self, request: CreatePaymentRequest) -> str:
        if request.payment_id in self.map:
            raise ValueError(f"Payment {request.payment_id} already exists")
        self.map[request.payment_id] = PaymentState.PENDING
        return f"example.com/payments/{request.payment_id}"

    async def create_payments(self, requests: list[CreatePaymentRequest]) -> None:
        for request in requests:
            self.map[request.payment_id] = PaymentState.PENDING

    async def get_states(self, payment_ids: list[str]) -> dict[str, PaymentState]:
        return {
            payment_id: self.map.get(payment_id, PaymentState.NONEXISTENT)
            for payment_id in payment_ids
        }

    async def start_refunds(self, payment_ids: list[str]) -> None:
        for payment_id in payment_ids:
            if self.map[payment_id] != PaymentState.PAID:
                raise ValueError(f"Payment {payment_id} is not paid")
            self.map[payment_id] = PaymentState.REFUNDING

    def pay_pending(self) -> None:
        for payment_id in self.map.keys():
            if self.map[payment_id] == PaymentState.PENDING:
                self.map[payment_id] = PaymentState.PAID

    def cancel_pending(self) -> None:
        for payment_id in self.map.keys():
            if self.map[payment_id] == PaymentState.PENDING:
                self.map[payment_id] = PaymentState.CANCELLED

    def start_refund_paid(self) -> None:
        for payment_id in self.map.keys():
            if self.map[payment_id] == PaymentState.PAID:
                self.map[payment_id] = PaymentState.REFUNDING

    def complete_refunding(self) -> None:
        for payment_id in self.map.keys():
            if self.map[payment_id] == PaymentState.REFUNDING:
                self.map[payment_id] = PaymentState.REFUNDED

    def fail_refund(self) -> None:
        for payment_id in self.map.keys():
            if self.map[payment_id] == PaymentState.REFUNDING:
                self.map[payment_id] = PaymentState.FAILED_REFUND
