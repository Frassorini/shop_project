from dishka import Provider, Scope, alias, provide

from shop_project.application.interfaces.interface_payment_gateway import (
    IPaymentGateway,
)
from shop_project.infrastructure.payments.inmemory_payment_gateway import (
    InMemoryPaymentGateway,
)


class PaymentProvider(Provider):
    scope = Scope.APP

    @provide
    def in_memory_payment_gateway(self) -> InMemoryPaymentGateway:
        return InMemoryPaymentGateway()

    payment_gateway = alias(InMemoryPaymentGateway, provides=IPaymentGateway)
