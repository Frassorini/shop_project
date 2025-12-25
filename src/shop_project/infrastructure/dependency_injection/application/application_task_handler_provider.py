from typing import Type

from dishka import Provider, Scope, provide

from shop_project.application.background.implementations.example_task_handler import (
    ExampleTaskHandler,
)
from shop_project.application.background.implementations.purchase_flow_handler import (
    BatchFinalizeNotPaidTasksHandler,
    BatchPaidReservationTimeOutTaskHandler,
    BatchWaitPaymentTaskHandler,
    BatchWaitRefundTaskHandler,
)
from shop_project.application.shared.interfaces.interface_payment_gateway import (
    IPaymentGateway,
)
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.domain.services.purchase_activation_service import (
    PurchaseActivationService,
)
from shop_project.domain.services.purchase_claim_service import PurchaseClaimService
from shop_project.domain.services.purchase_return_service import PurchaseReturnService


class ApplicationTaskHandlerProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def example_background_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> ExampleTaskHandler:
        return ExampleTaskHandler(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
        )

    @provide
    async def batch_wait_payment_task_handler(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        payment_gateway: IPaymentGateway,
    ) -> BatchWaitPaymentTaskHandler:
        return BatchWaitPaymentTaskHandler(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            purchase_activation_service=purchase_activation_service,
            purchase_claim_service=purchase_claim_service,
            purchase_return_service=purchase_return_service,
            payment_gateway=payment_gateway,
        )

    @provide
    async def batch_finalize_not_paid_tasks_handler(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        payment_gateway: IPaymentGateway,
    ) -> BatchFinalizeNotPaidTasksHandler:
        return BatchFinalizeNotPaidTasksHandler(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            purchase_activation_service=purchase_activation_service,
            purchase_claim_service=purchase_claim_service,
            purchase_return_service=purchase_return_service,
            payment_gateway=payment_gateway,
        )

    @provide
    async def batch_paid_reservation_time_out_task_handler(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        payment_gateway: IPaymentGateway,
    ) -> BatchPaidReservationTimeOutTaskHandler:
        return BatchPaidReservationTimeOutTaskHandler(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            purchase_activation_service=purchase_activation_service,
            purchase_claim_service=purchase_claim_service,
            purchase_return_service=purchase_return_service,
            payment_gateway=payment_gateway,
        )

    @provide
    async def batch_wait_refund_task_handler(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        payment_gateway: IPaymentGateway,
    ) -> BatchWaitRefundTaskHandler:
        return BatchWaitRefundTaskHandler(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            purchase_activation_service=purchase_activation_service,
            purchase_claim_service=purchase_claim_service,
            purchase_return_service=purchase_return_service,
            payment_gateway=payment_gateway,
        )
