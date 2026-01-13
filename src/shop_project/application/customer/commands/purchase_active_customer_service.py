from typing import Type
from uuid import UUID

from shop_project.application.customer.schemas.claim_token_schema import (
    ClaimTokenSchema,
)
from shop_project.application.customer.schemas.purchase_active_schema import (
    PurchaseActivationSchema,
    PurchaseActiveSchema,
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
    CreatePaymentRequest,
    IPaymentGateway,
)
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.application.shared.operation_log_payload_factories.purchase import (
    create_activate_purchase_payload,
    create_manual_unclaim_purchase_payload,
)
from shop_project.application.shared.policies.refund_initiation_policy import (
    RefundInitiationPolicy,
)
from shop_project.application.shared.scenarios.entity import get_one_or_raise_not_found
from shop_project.application.shared.scenarios.operation_log import log_operation
from shop_project.application.shared.scenarios.subject import (
    ensure_subject_type_or_raise_forbidden,
)
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.interfaces.subject import SubjectEnum
from shop_project.domain.services.purchase_activation_service import (
    PurchaseActivationService,
)
from shop_project.domain.services.purchase_claim_service import PurchaseClaimService
from shop_project.domain.services.purchase_return_service import PurchaseReturnService


class PurchaseActiveCustomerService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        purchase_activation_service: PurchaseActivationService,
        purchase_claim_service: PurchaseClaimService,
        purchase_return_service: PurchaseReturnService,
        payment_gateway: IPaymentGateway,
        claim_token_service: IClaimTokenService,
        refund_initiation_policy: RefundInitiationPolicy,
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
        self._refund_initiation_policy: RefundInitiationPolicy = (
            refund_initiation_policy
        )

    async def get_claim_token(
        self, access_payload: AccessTokenPayload
    ) -> ClaimTokenSchema:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.CUSTOMER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(ClaimToken)
            .from_id([access_payload.account_id])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            claim_token = resources.get_by_id_or_none(
                ClaimToken, access_payload.account_id
            )

            if claim_token:
                claim_token = claim_token
                token_raw = self._claim_token_service.refresh(claim_token)
            else:
                claim_token, token_raw = self._claim_token_service.create(
                    access_payload.account_id
                )

            resources.put(ClaimToken, claim_token)

            uow.mark_commit()

        return ClaimTokenSchema(claim_token=token_raw)

    async def activate_draft(
        self, access_payload: AccessTokenPayload, purchase_draft_id: UUID
    ) -> PurchaseActivationSchema:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.CUSTOMER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(PurchaseDraft)
            .from_id([purchase_draft_id])
            .and_()
            .from_attribute("customer_id", [access_payload.account_id])
            .for_update()
            .load(Product)
            .from_previous()
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            purchase_draft: PurchaseDraft = get_one_or_raise_not_found(
                resources, PurchaseDraft, purchase_draft_id
            )

            product_inventory = ProductInventory(resources.get_all(Product))

            activation = self._purchase_activation_service.activate(
                product_inventory=product_inventory, purchase_draft=purchase_draft
            )

            resources.delete(PurchaseDraft, purchase_draft)
            resources.put(PurchaseActive, activation.purchase_active)
            resources.put(EscrowAccount, activation.escrow_account)

            operation_log = create_activate_purchase_payload(
                access_token_payload=access_payload,
                purchase_active_dto=to_dto(activation.purchase_active),
                escrow_account_dto=to_dto(activation.escrow_account),
                product_dtos=[
                    to_dto(product) for product in resources.get_all(Product)
                ],
            )
            log_operation(resources, operation_log)

            uow.mark_commit()

        payment_request = CreatePaymentRequest(
            payment_id=str(activation.escrow_account.entity_id),
            amount=activation.escrow_account.total_amount,
        )

        payment_url = await self._payment_gateway.create_payment_and_get_url(
            payment_request
        )

        return PurchaseActivationSchema(
            purchase_active=PurchaseActiveSchema.create(
                to_dto(activation.purchase_active), to_dto(activation.escrow_account)
            ),
            payment_url=payment_url,
        )

    async def unclaim(
        self, access_payload: AccessTokenPayload, purchase_active_id: UUID
    ):
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.CUSTOMER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(EscrowAccount)
            .from_id([purchase_active_id])
            .for_update()
            .load(PurchaseActive)
            .from_previous()
            .and_()
            .from_attribute("customer_id", [access_payload.account_id])
            .for_update()
            .load(Product)
            .from_previous()
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            purchase_active = get_one_or_raise_not_found(
                resources, PurchaseActive, purchase_active_id
            )
            escrow_account = get_one_or_raise_not_found(
                resources, EscrowAccount, purchase_active_id
            )

            summary = self._purchase_return_service.unclaim(
                product_inventory=ProductInventory(resources.get_all(Product)),
                purchase_active=purchase_active,
                escrow_account=escrow_account,
            )

            resources.delete(PurchaseActive, purchase_active)
            resources.put(PurchaseSummary, summary)

            operation_log = create_manual_unclaim_purchase_payload(
                access_token_payload=access_payload,
                purchase_summary_dto=to_dto(summary),
                escrow_account_dto=to_dto(escrow_account),
            )
            log_operation(resources, operation_log)

            uow.mark_commit()

        if self._refund_initiation_policy.start_immediately:
            await self._payment_gateway.start_refunds([str(escrow_account.entity_id)])

        return PurchaseSummarySchema.create(to_dto(summary), to_dto(escrow_account))
