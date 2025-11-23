from decimal import Decimal
from uuid import uuid4

from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.exceptions import DomainException
from shop_project.domain.helpers.product_inventory import ProductInventory


class CheckoutService:
    def _count_total_price(
        self, product_inventory: ProductInventory, purchase_draft: PurchaseDraft
    ) -> Decimal:
        total_price = Decimal(0)
        for item in purchase_draft.get_items():
            total_price += (
                product_inventory.get_item(item.product_id).price * item.amount
            )
        return total_price

    def checkout(
        self, product_inventory: ProductInventory, purchase_draft: PurchaseDraft
    ) -> EscrowAccount:
        if purchase_draft.is_finalized():
            raise DomainException("Cannot checkout finalized draft")

        total_price = self._count_total_price(
            product_inventory=product_inventory, purchase_draft=purchase_draft
        )

        if total_price <= 0:
            raise DomainException("Total price must be > 0")

        escrow_account = EscrowAccount(uuid4(), total_price)

        return escrow_account
