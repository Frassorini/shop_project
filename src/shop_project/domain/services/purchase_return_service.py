from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.domain.exceptions import DomainInvalidStateError
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.purchase_summary_service import PurchaseSummaryService


class PurchaseReturnService:
    def __init__(self, purchase_summary_service: PurchaseSummaryService) -> None:
        self._purchase_summary_service: PurchaseSummaryService = (
            purchase_summary_service
        )

    def handle_cancelled_payment(
        self,
        product_inventory: ProductInventory,
        purchase_active: PurchaseActive,
        escrow_account: EscrowAccount,
    ) -> PurchaseSummary:
        if purchase_active.is_finalized():
            raise DomainInvalidStateError("Cannot cancel finalized purchase")

        if not escrow_account.is_payment_cancelled():
            raise DomainInvalidStateError(
                "Cannot cancel purchase with un-cancelled escrow account"
            )

        escrow_account.finalize()

        product_inventory.restock(purchase_active.items)

        return self._purchase_summary_service.finalize_cancel_payment(purchase_active)

    def unclaim(
        self,
        product_inventory: ProductInventory,
        purchase_active: PurchaseActive,
        escrow_account: EscrowAccount,
    ) -> PurchaseSummary:
        if purchase_active.is_finalized():
            raise DomainInvalidStateError("Cannot unclaim finalized purchase")

        if not escrow_account.is_paid():
            raise DomainInvalidStateError(
                "Cannot unclaim purchase with un-paid escrow account"
            )

        escrow_account.begin_refund()

        product_inventory.restock(purchase_active.items)

        return self._purchase_summary_service.finalize_unclaim(purchase_active)
