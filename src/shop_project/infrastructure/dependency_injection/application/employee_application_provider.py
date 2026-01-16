from typing import Type

from dishka import Provider, Scope, provide

from shop_project.application.employee.commands.purchase_active_employee_service import (
    PurchaseActiveEmployeeService,
)
from shop_project.application.shared.interfaces.interface_claim_token_service import (
    IClaimTokenService,
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


class EmployeeApplicationProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def purchase_active_employee_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        claim_token_service: IClaimTokenService,
    ) -> PurchaseActiveEmployeeService:
        return PurchaseActiveEmployeeService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            purchase_activation_service=purchase_activation_service,
            purchase_claim_service=purchase_claim_service,
            purchase_return_service=purchase_return_service,
            claim_token_service=claim_token_service,
        )
