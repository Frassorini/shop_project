from shop_project.domain.purchase_active import PurchaseActive, PurchaseActiveItem
from shop_project.domain.purchase_summary import PurchaseSummary, PurchaseSummaryItem, PurchaseSummaryReason
from shop_project.domain.exceptions import DomainException
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.shared.entity_id import EntityId


class PurchaseSummaryService():
    def __init__(self) -> None:
        pass
    
    def finalize_cancel_payment(self, purchase: PurchaseActive) -> PurchaseSummary:
        return self._finalize(purchase, PurchaseSummaryReason.PAYMENT_CANCELLED)
    
    def finalize_claim(self, purchase: PurchaseActive) -> PurchaseSummary:
        return self._finalize(purchase, PurchaseSummaryReason.CLAIMED)
    
    def finalize_unclaim(self, purchase: PurchaseActive) -> PurchaseSummary:
        return self._finalize(purchase, PurchaseSummaryReason.NOT_CLAIMED)
    
    def _finalize(self, purchase: PurchaseActive, reason: PurchaseSummaryReason) -> PurchaseSummary:
        if purchase.is_finalized():
            raise DomainException('Cannot finalize finalized purchase')
        
        purchase_summary_items: list[PurchaseSummaryItem] = []
        
        for item in purchase.get_items():
            purchase_summary_items.append(
                PurchaseSummaryItem(
                    product_id=item.product_id, 
                    amount=item.amount, 
                )
            )
        
        purchase_summary = PurchaseSummary(
            customer_id=purchase.customer_id,
            entity_id=EntityId.get_random(),
            escrow_account_id=purchase.escrow_account_id,
            reason=reason,
            items=purchase_summary_items
        )
        
        purchase.finalize()
        
        return purchase_summary