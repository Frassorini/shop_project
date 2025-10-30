from decimal import Decimal
from shop_project.domain.escrow_account import EscrowAccount
from shop_project.domain.purchase_active import PurchaseActive, PurchaseActiveItem
from shop_project.domain.exceptions import DomainException
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.services.inventory_service import InventoryService
from shop_project.shared.entity_id import EntityId


class CheckoutService():
    def __init__(self, inventory_service: InventoryService) -> None:
        self._inventory_service: InventoryService = inventory_service
        
    def _count_total_price(self, purchase_draft: PurchaseDraft) -> Decimal:
        total_price = Decimal(0)
        for item in purchase_draft.get_items():
            total_price += self._inventory_service.get_item(item.product_id).price * item.amount
        return total_price

    def checkout(self, purchase_draft: PurchaseDraft) -> EscrowAccount:
        if purchase_draft.is_finalized():
            raise DomainException('Cannot checkout finalized draft')
        
        total_price = self._count_total_price(purchase_draft)
        
        if total_price <= 0:
            raise DomainException('Total price must be > 0')
        
        escrow_account = EscrowAccount(EntityId.get_random(), total_price)
        
        return escrow_account