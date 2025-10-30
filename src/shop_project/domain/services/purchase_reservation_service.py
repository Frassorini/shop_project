from shop_project.domain.escrow_account import EscrowAccount
from shop_project.domain.purchase_active import PurchaseActive, PurchaseActiveItem
from shop_project.domain.exceptions import DomainException
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.purchase_summary import PurchaseSummary, PurchaseSummaryItem, PurchaseSummaryReason
from shop_project.domain.services.inventory_service import InventoryService
from shop_project.shared.entity_id import EntityId


class PurchaseReservationService():
    def __init__(self, inventory_service: InventoryService) -> None:
        self._inventory_service: InventoryService = inventory_service

    def reserve(self, purchase_draft: PurchaseDraft, escrow_account: EscrowAccount) -> PurchaseActive:
        self._inventory_service.reserve_stock(purchase_draft.get_items())
        
        purchase_active_items: list[PurchaseActiveItem] = []
        
        for item in purchase_draft.get_items():
            purchase_active_items.append(
                PurchaseActiveItem(
                    product_id=item.product_id, 
                    amount=item.amount, 
                )
            )
        
        purchase_active = PurchaseActive(
            customer_id=purchase_draft.customer_id,
            entity_id=EntityId.get_random(),
            escrow_account_id=escrow_account.entity_id,
            items=purchase_active_items
        )
        
        return purchase_active
    