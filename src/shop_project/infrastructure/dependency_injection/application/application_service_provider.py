from typing import Type

from dishka import Provider, Scope, provide

from shop_project.application.authentication.commands.authentication_service import (
    AuthenticationService,
)
from shop_project.application.authentication.commands.registration_service import (
    RegistrationService,
)
from shop_project.application.authentication.commands.totp_challenge_service import (
    TotpChallengeService,
)
from shop_project.application.customer.commands.customer_service import CustomerService
from shop_project.application.customer.commands.purchase_flow_service import (
    PurchaseFlowService,
)
from shop_project.application.shared.interfaces.interface_account_service import (
    IAccountService,
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
from shop_project.application.shared.interfaces.interface_session_service import (
    ISessionService,
)
from shop_project.application.shared.interfaces.interface_totp_service import (
    ITotpService,
)
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.domain.services.purchase_activation_service import (
    PurchaseActivationService,
)
from shop_project.domain.services.purchase_claim_service import PurchaseClaimService
from shop_project.domain.services.purchase_return_service import PurchaseReturnService


class ApplicationServiceProvider(Provider):
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
    async def register_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        account_service: IAccountService,
        totp_service: ITotpService,
        session_service: ISessionService,
    ) -> RegistrationService:
        return RegistrationService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            account_service=account_service,
            totp_service=totp_service,
            session_service=session_service,
        )

    @provide
    async def authentication_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        account_service: IAccountService,
        totp_service: ITotpService,
        session_service: ISessionService,
    ) -> AuthenticationService:
        return AuthenticationService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            account_service=account_service,
            totp_service=totp_service,
            session_service=session_service,
        )

    @provide
    async def totp_challenge_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        totp_service: ITotpService,
    ) -> TotpChallengeService:
        return TotpChallengeService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            totp_service=totp_service,
        )

    @provide
    async def purchase_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        payment_gateway: IPaymentGateway,
        claim_token_service: IClaimTokenService,
    ) -> PurchaseFlowService:
        return PurchaseFlowService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            purchase_activation_service=purchase_activation_service,
            purchase_claim_service=purchase_claim_service,
            purchase_return_service=purchase_return_service,
            payment_gateway=payment_gateway,
            claim_token_service=claim_token_service,
        )
