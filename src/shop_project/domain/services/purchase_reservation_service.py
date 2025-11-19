from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.purchase_active import (
    PurchaseActive,
    PurchaseActiveItem,
)
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.shared.entity_id import EntityId


class PurchaseReservationService:
    def reserve(
        self,
        product_inventory: ProductInventory,
        purchase_draft: PurchaseDraft,
        escrow_account: EscrowAccount,
    ) -> PurchaseActive:
        product_inventory.reserve_stock(purchase_draft.get_items())

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
            items=purchase_active_items,
        )

        return purchase_active
