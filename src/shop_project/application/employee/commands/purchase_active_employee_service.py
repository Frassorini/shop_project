from typing import Type

from shop_project.application.customer.schemas.claim_token_schema import (
    ClaimTokenSchema,
)
from shop_project.application.customer.schemas.purchase_summary_schema import (
    PurchaseSummarySchema,
)
from shop_project.application.entities.claim_token import ClaimToken
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.dto.mapper import to_dto
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
from shop_project.application.shared.scenarios.entity import (
    get_one_or_raise_forbidden,
)
from shop_project.application.shared.scenarios.purchase import (
    get_escrow_purchase_active_map,
)
from shop_project.application.shared.scenarios.subject import (
    ensure_subject_type_or_raise_forbidden,
)
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.domain.interfaces.subject import SubjectEnum
from shop_project.domain.services.purchase_activation_service import (
    PurchaseActivationService,
)
from shop_project.domain.services.purchase_claim_service import PurchaseClaimService
from shop_project.domain.services.purchase_return_service import PurchaseReturnService


class PurchaseActiveEmployeeService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        payment_gateway: IPaymentGateway,
        claim_token_service: IClaimTokenService,
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type
        self._purchase_activation_service: PurchaseActivationService = (
            purchase_activation_service
        )
        self._purchase_claim_service: PurchaseClaimService = purchase_claim_service
        self._purchase_return_service: PurchaseReturnService = purchase_return_service
        self._payment_gateway: IPaymentGateway = payment_gateway
        self._claim_token_service: IClaimTokenService = claim_token_service

    async def claim(
        self, access_payload: AccessTokenPayload, claim_token: ClaimTokenSchema
    ) -> list[PurchaseSummarySchema]:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.EMPLOYEE)
        token_fingerprint = self._claim_token_service.get_claim_token_fingerprint(
            claim_token.claim_token
        )

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(ClaimToken)
            .from_attribute("token_fingerprint", [token_fingerprint])
            .for_update()
            .load(Employee)
            .from_id([access_payload.account_id])
            .for_share()
            .load(Customer)
            .from_previous(0)
            .for_share()
            .load(EscrowAccount)
            .from_previous(2)
            .for_update()
            .load(PurchaseActive)
            .from_previous(3)
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            employee = get_one_or_raise_forbidden(
                resources, Employee, access_payload.account_id
            )
            escrow_accounts = resources.get_all(EscrowAccount)
            purchases = resources.get_all(PurchaseActive)

            escrow_purchase_map = get_escrow_purchase_active_map(resources)

            summaries_with_escrows: list[tuple[PurchaseSummary, EscrowAccount]] = []
            for escrow, purchase in escrow_purchase_map:
                summary = self._purchase_claim_service.claim(
                    employee=employee, purchase_active=purchase, escrow_account=escrow
                )

                resources.delete(PurchaseActive, purchase)
                resources.put(PurchaseSummary, summary)
                summaries_with_escrows.append((summary, escrow))

            uow.mark_commit()

        result: list[PurchaseSummarySchema] = []
        for summary, escrow_account in summaries_with_escrows:
            result.append(
                PurchaseSummarySchema.create(
                    purchase_summary_dto=to_dto(summary),
                    escrow_account_dto=to_dto(escrow_account),
                )
            )

        return result
