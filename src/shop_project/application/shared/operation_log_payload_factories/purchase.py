from shop_project.application.entities.operation_log.operation_log_payload_implementations.purchase import (
    ActivatePurchaseItem,
    ActivatePurchaseOperationLogPayload,
    AutoUnclaimPurchaseOperationLogPayload,
    CancelPurchaseOperationLogPayload,
    ClaimPurchaseOperationLogPayload,
    ManualUnclaimPurchaseOperationLogPayload,
    PayPurchaseOperationLogPayload,
    RefundPurchaseOperationLogPayload,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.dto.escrow_account_dto import EscrowAccountDTO
from shop_project.application.shared.dto.product_dto import ProductDTO
from shop_project.application.shared.dto.purchase_active_dto import PurchaseActiveDTO
from shop_project.application.shared.dto.purchase_summary_dto import PurchaseSummaryDTO


def create_activate_purchase_payload(
    access_token_payload: AccessTokenPayload,
    purchase_active_dto: PurchaseActiveDTO,
    escrow_account_dto: EscrowAccountDTO,
    product_dtos: list[ProductDTO],
) -> ActivatePurchaseOperationLogPayload:
    items: list[ActivatePurchaseItem] = []

    for purchase_item_dto in purchase_active_dto.items:
        added = False
        for product_dto in product_dtos:
            if product_dto.entity_id == purchase_item_dto.product_id:
                items.append(
                    ActivatePurchaseItem(
                        product_id=product_dto.entity_id,
                        amount=purchase_item_dto.amount,
                        price=product_dto.price,
                    )
                )
                added = True
                break
        if not added:
            raise RuntimeError(
                f"Product with id {purchase_item_dto.product_id} not found in product_dtos"
            )

    return ActivatePurchaseOperationLogPayload(
        subject_type=access_token_payload.subject_type,
        subject_id=access_token_payload.account_id,
        purchase_id=purchase_active_dto.entity_id,
        items=items,
        total_amount=escrow_account_dto.total_amount,
    )


def create_pay_purchase_payload(
    escrow_account_dto: EscrowAccountDTO,
) -> PayPurchaseOperationLogPayload:
    return PayPurchaseOperationLogPayload(
        purchase_id=escrow_account_dto.entity_id,
        amount=escrow_account_dto.total_amount,
        currency="RUB",
        payment_method="card",
    )


def create_claim_purchase_payload(
    access_token_payload: AccessTokenPayload, escrow_account_dto: EscrowAccountDTO
) -> ClaimPurchaseOperationLogPayload:
    return ClaimPurchaseOperationLogPayload(
        subject_type=access_token_payload.subject_type,
        subject_id=access_token_payload.account_id,
        purchase_id=escrow_account_dto.entity_id,
    )


def create_manual_unclaim_purchase_payload(
    purchase_summary_dto: PurchaseSummaryDTO, escrow_account_dto: EscrowAccountDTO
) -> ManualUnclaimPurchaseOperationLogPayload:
    return ManualUnclaimPurchaseOperationLogPayload(
        purchase_id=escrow_account_dto.entity_id,
        reason=purchase_summary_dto.reason,
    )


def create_auto_unclaim_purchase_payload(
    purchase_summary_dto: PurchaseSummaryDTO, escrow_account_dto: EscrowAccountDTO
) -> AutoUnclaimPurchaseOperationLogPayload:
    return AutoUnclaimPurchaseOperationLogPayload(
        purchase_id=escrow_account_dto.entity_id,
        reason=purchase_summary_dto.reason,
    )


def create_refund_purchase_payload(
    escrow_account_dto: EscrowAccountDTO,
) -> RefundPurchaseOperationLogPayload:
    return RefundPurchaseOperationLogPayload(
        purchase_id=escrow_account_dto.entity_id,
        amount=escrow_account_dto.total_amount,
    )


def create_cancel_purchase_payload(
    escrow_account_dto: EscrowAccountDTO,
) -> CancelPurchaseOperationLogPayload:
    return CancelPurchaseOperationLogPayload(
        purchase_id=escrow_account_dto.entity_id,
    )
