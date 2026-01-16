from datetime import datetime, timedelta, timezone

from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.purchase_active import (
    PurchaseActive,
    PurchaseActiveItem,
)
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.helpers.product_inventory import ProductInventory


class PurchaseReservationService:
    def __init__(self, purchase_reservation_ttl: timedelta) -> None:
        self._purchase_reservation_ttl = purchase_reservation_ttl

    def reserve(
        self,
        product_inventory: ProductInventory,
        purchase_draft: PurchaseDraft,
        escrow_account: EscrowAccount,
    ) -> PurchaseActive:
        product_inventory.reserve_stock(purchase_draft.items)

        purchase_active_items: list[PurchaseActiveItem] = []

        for item in purchase_draft.items:
            purchase_active_items.append(
                PurchaseActiveItem(
                    product_id=item.product_id,
                    amount=item.amount,
                )
            )

        purchase_active = PurchaseActive(
            customer_id=purchase_draft.customer_id,
            entity_id=escrow_account.entity_id,
            escrow_account_id=escrow_account.entity_id,
            items=purchase_active_items,
            reserved_until=datetime.now(tz=timezone.utc)
            + self._purchase_reservation_ttl,
        )

        return purchase_active
