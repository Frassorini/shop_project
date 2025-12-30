from typing import Type

from dishka import Provider, Scope, provide

from shop_project.application.authentication.adapters.access_token_verifier import (
    AccessTokenVerifier,
)
from shop_project.application.authentication.commands.account_service import (
    AccountService,
)
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
from shop_project.application.employee.commands.purchase_active_employee_service import (
    PurchaseActiveEmployeeService,
)
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
from shop_project.domain.services.shipment_activation_service import (
    ShipmentActivationService,
)
from shop_project.domain.services.shipment_cancel_service import ShipmentCancelService
from shop_project.domain.services.shipment_receive_service import ShipmentReceiveService


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
    async def purchase_active_customer_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        payment_gateway: IPaymentGateway,
        claim_token_service: IClaimTokenService,
    ) -> PurchaseActiveCustomerService:
        return PurchaseActiveCustomerService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            purchase_activation_service=purchase_activation_service,
            purchase_claim_service=purchase_claim_service,
            purchase_return_service=purchase_return_service,
            payment_gateway=payment_gateway,
            claim_token_service=claim_token_service,
        )

    @provide
    async def purchase_active_employee_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        payment_gateway: IPaymentGateway,
        claim_token_service: IClaimTokenService,
    ) -> PurchaseActiveEmployeeService:
        return PurchaseActiveEmployeeService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            purchase_activation_service=purchase_activation_service,
            purchase_claim_service=purchase_claim_service,
            purchase_return_service=purchase_return_service,
            payment_gateway=payment_gateway,
            claim_token_service=claim_token_service,
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

    @provide
    async def product_manager_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> ProductManagerService:
        return ProductManagerService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
        )

    @provide
    async def shipment_manager_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        shipment_activation_service: ShipmentActivationService,
        shipment_cancel_service: ShipmentCancelService,
        shipment_receive_service: ShipmentReceiveService,
    ) -> ShipmentManagerService:
        return ShipmentManagerService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            shipment_activation_service=shipment_activation_service,
            shipment_cancel_service=shipment_cancel_service,
            shipment_receive_service=shipment_receive_service,
        )

    @provide
    async def operation_log_read_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> OperationLogReadService:
        return OperationLogReadService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
        )

    @provide
    async def employee_manager_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> EmployeeManagerService:
        return EmployeeManagerService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
        )

    @provide
    async def employee_manager_read_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> EmployeeManagerReadService:
        return EmployeeManagerReadService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
        )

    @provide
    async def account_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        account_service: IAccountService,
        totp_service: ITotpService,
        session_service: ISessionService,
    ) -> AccountService:
        return AccountService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            account_service=account_service,
            totp_service=totp_service,
            session_service=session_service,
        )

    @provide
    async def access_token_verifier(
        self,
        session_service: ISessionService,
    ) -> AccessTokenVerifier:
        return AccessTokenVerifier(
            session_service=session_service,
        )
