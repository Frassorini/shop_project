from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.domain.exceptions import DomainException
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.purchase_summary_service import PurchaseSummaryService


class PurchaseReturnService:
    def __init__(self, purchase_summary_service: PurchaseSummaryService) -> None:
        self._purchase_summary_service: PurchaseSummaryService = (
            purchase_summary_service
        )

    def payment_cancel(
        self,
        product_inventory: ProductInventory,
        purchase_active: PurchaseActive,
        escrow_account: EscrowAccount,
    ) -> PurchaseSummary:
        if purchase_active.is_finalized():
            raise DomainException("Cannot cancel finalized purchase")

        if not escrow_account.is_cancelled():
            raise DomainException("Escrow account is not cancelled")

        escrow_account.finalize()

        product_inventory.restock(purchase_active.get_items())

        return self._purchase_summary_service.finalize_cancel_payment(purchase_active)

    def unclaim(
        self,
        product_inventory: ProductInventory,
        purchase_active: PurchaseActive,
        escrow_account: EscrowAccount,
    ) -> PurchaseSummary:
        if purchase_active.is_finalized():
            raise DomainException("Cannot unclaim finalized purchase")

        if not escrow_account.is_ready_for_refund():
            raise DomainException("Escrow account is not ready for refund")

        escrow_account.begin_refund()

        product_inventory.restock(purchase_active.get_items())

        return self._purchase_summary_service.finalize_unclaim(purchase_active)
