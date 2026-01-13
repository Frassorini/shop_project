from typing import Type

from dishka import Provider, Scope, provide

from shop_project.application.customer.commands.customer_service import CustomerService
from shop_project.application.customer.commands.purchase_active_customer_service import (
    PurchaseActiveCustomerService,
)
from shop_project.application.customer.commands.purchase_draft_customer_service import (
    PurchaseDraftCustomerService,
)
from shop_project.application.customer.queries.catalogue_customer_read_service import (
    CatalogueCustomerReadService,
)
from shop_project.application.customer.queries.purchase_customer_read_service import (
    PurchaseCustomerReadService,
)
from shop_project.application.shared.interfaces.interface_claim_token_service import (
    IClaimTokenService,
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
from shop_project.application.shared.policies.refund_initiation_policy import (
    RefundInitiationPolicy,
)
from shop_project.domain.services.purchase_activation_service import (
    PurchaseActivationService,
)
from shop_project.domain.services.purchase_claim_service import PurchaseClaimService
from shop_project.domain.services.purchase_return_service import PurchaseReturnService


class CustomerApplicationProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def customer_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> CustomerService:
        return CustomerService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
        )

    @provide
    async def purchase_active_customer_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        payment_gateway: IPaymentGateway,
        claim_token_service: IClaimTokenService,
        refund_initiation_policy: RefundInitiationPolicy,
    ) -> PurchaseActiveCustomerService:
        return PurchaseActiveCustomerService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            purchase_activation_service=purchase_activation_service,
            purchase_claim_service=purchase_claim_service,
            purchase_return_service=purchase_return_service,
            payment_gateway=payment_gateway,
            claim_token_service=claim_token_service,
            refund_initiation_policy=refund_initiation_policy,
        )

    @provide
    async def purchase_draft_customer_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> PurchaseDraftCustomerService:
        return PurchaseDraftCustomerService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
        )

    @provide
    async def purchase_customer_read_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> PurchaseCustomerReadService:
        return PurchaseCustomerReadService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
        )

    @provide
    async def catalogue_customer_read_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> CatalogueCustomerReadService:
        return CatalogueCustomerReadService(
            unit_of_work_factory,
            query_builder_type,
        )
