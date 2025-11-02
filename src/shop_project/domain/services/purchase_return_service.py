from shop_project.domain.escrow_account import EscrowAccount, EscrowState
from shop_project.domain.purchase_active import PurchaseActive, PurchaseActiveItem
from shop_project.domain.exceptions import DomainException
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.purchase_summary import PurchaseSummary, PurchaseSummaryItem, PurchaseSummaryReason
from shop_project.domain.product_inventory import ProductInventory
from shop_project.domain.services.purchase_summary_service import PurchaseSummaryService
from shop_project.shared.entity_id import EntityId


class PurchaseReturnService():
    def __init__(self, purchase_summary_service: PurchaseSummaryService) -> None:
        self._purchase_summary_service: PurchaseSummaryService = purchase_summary_service

    def payment_cancel(self, product_inventory: ProductInventory, purchase_active: PurchaseActive, escrow_account: EscrowAccount) -> PurchaseSummary:
        if purchase_active.is_finalized():
            raise DomainException('Cannot cancel finalized purchase')
        
        if not escrow_account.is_pending():
            raise DomainException('Escrow account is not pending')
        
        escrow_account.finalize()
        
        product_inventory.restock(purchase_active.get_items())
        
        return self._purchase_summary_service.finalize_cancel_payment(purchase_active)

    def unclaim(self, product_inventory: ProductInventory, purchase_active: PurchaseActive, escrow_account: EscrowAccount) -> PurchaseSummary:
        if purchase_active.is_finalized():
            raise DomainException('Cannot unclaim finalized purchase')
        
        if not escrow_account.is_paid():
            raise DomainException('Escrow account is not pending')
        
        escrow_account.begin_refund()
        
        product_inventory.restock(purchase_active.get_items())
        
        return self._purchase_summary_service.finalize_unclaim(purchase_active)
