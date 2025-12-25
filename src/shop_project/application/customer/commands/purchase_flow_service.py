from collections import defaultdict
from typing import Any, Type
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
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.purchase_activation_service import (
    PurchaseActivationService,
)
from shop_project.domain.services.purchase_claim_service import PurchaseClaimService
from shop_project.domain.services.purchase_return_service import PurchaseReturnService
from shop_project.infrastructure.entities.claim_token import ClaimToken


class PurchaseFlowService:
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

    async def get_claim_token(self, customer_id: UUID) -> ClaimTokenSchema:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(ClaimToken)
            .from_id([customer_id])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resorces()
            maybe_claim_token_lst = resources.get_all(ClaimToken)

            if maybe_claim_token_lst:
                claim_token = maybe_claim_token_lst[0]
                token_raw = self._claim_token_service.refresh()
            else:
                claim_token, token_raw = self._claim_token_service.create(customer_id)

            resources.put(ClaimToken, claim_token)

            uow.mark_commit()

        return ClaimTokenSchema(claim_token=token_raw)

    async def activate_draft(
        self, customer_id: UUID, purchase_draft_id: UUID
    ) -> PurchaseActivationSchema:
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(PurchaseDraft)
            .from_id([purchase_draft_id])
            .and_()
            .from_attribute("customer_id", [customer_id])
            .for_update()
            .load(Product)
            .from_previous()
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resorces()
            purchase_draft: PurchaseDraft = resources.get_by_id(
                PurchaseDraft, purchase_draft_id
            )

            product_inventory = ProductInventory(resources.get_all(Product))

            activation = self._purchase_activation_service.activate(
                product_inventory=product_inventory, purchase_draft=purchase_draft
            )

            resources.delete(PurchaseDraft, purchase_draft)
            resources.put(PurchaseActive, activation.purchase_active)
            resources.put(EscrowAccount, activation.escrow_account)

            assert (
                activation.purchase_active.entity_id
                == activation.escrow_account.entity_id
            )

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

    async def claim(self, claim_token: str) -> list[PurchaseSummarySchema]:
        token_fingerprint = self._claim_token_service.get_claim_token_fingerprint(
            claim_token
        )

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(ClaimToken)
            .from_attribute("token_fingerprint", [token_fingerprint])
            .for_update()
            .load(Customer)
            .from_previous()
            .for_share()
            .load(EscrowAccount)
            .from_previous()
            .for_update()
            .load(PurchaseActive)
            .from_previous()
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resorces()
            escrow_accounts = resources.get_all(EscrowAccount)
            purchases = resources.get_all(PurchaseActive)

            escrow_purchase_map: dict[UUID, list[Any]] = defaultdict(
                lambda: [None, None]
            )

            for escrow_account in escrow_accounts:
                escrow_purchase_map[escrow_account.entity_id][0] = escrow_account

            for purchase in purchases:
                escrow_purchase_map[purchase.entity_id][1] = purchase

            summaries_with_escrows: list[tuple[PurchaseSummary, EscrowAccount]] = []

            for escrow, purchase in escrow_purchase_map.values():
                if not purchase:
                    continue

                assert isinstance(purchase, PurchaseActive)
                assert isinstance(escrow, EscrowAccount)

                summary = self._purchase_claim_service.claim(
                    purchase_active=purchase, escrow_account=escrow
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

    async def unclaim(self, customer_id: UUID, purchase_active_id: UUID):
        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(EscrowAccount)
            .from_id([purchase_active_id])
            .for_update()
            .load(PurchaseActive)
            .from_previous()
            .and_()
            .from_attribute("customer_id", [customer_id])
            .for_update()
            .load(Product)
            .from_previous()
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resorces()
            purchase_active = resources.get_by_id(PurchaseActive, purchase_active_id)
            escrow_account = resources.get_by_id(EscrowAccount, purchase_active_id)

            summary = self._purchase_return_service.unclaim(
                product_inventory=ProductInventory(resources.get_all(Product)),
                purchase_active=purchase_active,
                escrow_account=escrow_account,
            )

            resources.delete(PurchaseActive, purchase_active)
            resources.put(PurchaseSummary, summary)

            uow.mark_commit()

        await self._payment_gateway.start_refunds([str(escrow_account.entity_id)])

        return PurchaseSummarySchema.create(to_dto(summary), to_dto(escrow_account))
