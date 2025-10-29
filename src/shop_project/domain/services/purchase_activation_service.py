from dataclasses import dataclass
from shop_project.domain import purchase_active
from shop_project.domain.escrow_account import EscrowAccount
from shop_project.domain.purchase_active import PurchaseActive, PurchaseActiveItem
from shop_project.domain.exceptions import DomainException
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.purchase_summary import PurchaseSummary, PurchaseSummaryItem, PurchaseSummaryReason
from shop_project.domain.services.inventory_service import InventoryService
from shop_project.domain.services.checkout_service import CheckoutService
from shop_project.domain.services.purchase_reservation_service import PurchaseReservationService
from shop_project.shared.entity_id import EntityId

@dataclass(frozen=True)
class PurchaseActivation:
    purchase_active: PurchaseActive
    escrow_account: EscrowAccount


class PurchaseActivationService():
    def __init__(self, inventory_service: InventoryService, 
                 purchase_reservation_service: PurchaseReservationService, 
                 checkout_service: CheckoutService) -> None:
        self._inventory_service: InventoryService = inventory_service
        self._purchase_reservation_service: PurchaseReservationService = purchase_reservation_service
        self._checkout_service: CheckoutService = checkout_service

    def activate(self, purchase_draft: PurchaseDraft) -> PurchaseActivation:
        if purchase_draft.is_finalized():
            raise DomainException('Cannot activate finalized draft')
        
        escrow_account = self._checkout_service.checkout(purchase_draft)
        purchase_active = self._purchase_reservation_service.reserve(purchase_draft, escrow_account)
        escrow_account.attach_to_purchase(purchase_active.entity_id)
        purchase_draft.finalize()
        
        return PurchaseActivation(purchase_active, escrow_account)
