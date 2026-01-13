from typing import Type

from dishka import Provider, Scope, provide

from shop_project.application.payments.commands.payment_service import PaymentService
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.domain.services.purchase_return_service import PurchaseReturnService


class PaymentApplicationProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def payment_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_return_service: PurchaseReturnService,
    ) -> PaymentService:
        return PaymentService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            purchase_return_service=purchase_return_service,
        )
